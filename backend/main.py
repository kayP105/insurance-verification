import os
import shutil
import uvicorn
import joblib
import pandas as pd
import shap
import re
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import engine, SessionLocal
from models import Base, Document, MockInsurerPolicy, User
from datetime import datetime
from rules import *  
from duplicate_detection import is_duplicate_claim
from fraud_graph import build_fraud_graph, graph_to_json
from ocr_module import extract_structured_data, extract_entities_with_spacy, process_document
from layout_models import extract_layout_entities
from image_forensics import tamper_score_image
from data.rag_chatbot import query_rag_chatbot
from rapidfuzz import fuzz
from durable.lang import post as post_to_ruleset
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException  
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token, decode_token
from crypto_utils import encrypt_field, decrypt_field


UPLOAD_DIR = "./uploaded_files"  
os.makedirs(UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


uploaded_files_dir = os.path.join(os.path.dirname(__file__), "uploaded_files")
os.makedirs(uploaded_files_dir, exist_ok=True)  # Fixed: was uploads_dir
app.mount("/uploads", StaticFiles(directory=uploaded_files_dir), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class VerificationRequest(BaseModel):
    policy_no: str
    name: str
    claim_amount: float

class EligibilityRequest(BaseModel):
    features: dict

class WorkflowRequest(BaseModel):
    doc_id: int
    claim_amount: float

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
  

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class UserOut(BaseModel):
    username: str
    email: str
    role: str


@app.post("/rag_chat")
async def rag_chat(request: Request):
    data = await request.json()
    user_query = data.get("query")
    if not user_query or user_query.strip() == "":
        return {"answer": "Please enter a valid question."}
    answer = query_rag_chatbot(user_query)
    return {"answer": answer}


@app.post("/upload")
def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    db = SessionLocal()
    
   
    new_doc = Document(filename=file.filename, local_path="", status="pending_upload")
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    
    filename_parts = file.filename.rsplit('.', 1)
    if len(filename_parts) == 2:
        unique_filename = f"doc_{new_doc.id}_{filename_parts[0]}.{filename_parts[1]}"
    else:
        unique_filename = f"doc_{new_doc.id}_{file.filename}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    
    new_doc.local_path = f"/uploads/{unique_filename}" 
    new_doc.status = "pending_ocr" # 
    db.commit()
    
    background_tasks.add_task(process_document, new_doc.id, file_path)
    db.close()
    
    return {"message": f"File '{file.filename}' uploaded and OCR started.", "doc_id": new_doc.id}

@app.get("/status/{doc_id}")
def get_status(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "Document not found"}
    return {"id": doc.id, "filename": doc.filename, "status": doc.status, "data": doc.extracted_json}

@app.get("/claims")
def get_all_claims(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    claims = [
        {
            "id": d.id,
            "filename": d.filename,
            "status": d.status,
            "tamper_score": d.extracted_json.get("tamper_score") if d.extracted_json else None,
            "duplicates": d.extracted_json.get("duplicate_check", {}).get("similar_docs", []) if d.extracted_json else None,
            "agent_decision": d.agent_decision,
            "agent_notes": d.agent_notes,
            "workflow_decision": d.extracted_json.get("workflow_decision") if d.extracted_json else None,
        } for d in docs
    ]
    return {"claims": claims}
@app.get("/claims/{doc_id}")
def get_claim_by_id(doc_id: int, db: Session = Depends(get_db)):
    """Get single claim details by ID"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "local_path": doc.local_path,
        "status": doc.status,
        "extracted_json": doc.extracted_json,
        "agent_notes": doc.agent_notes,
        "agent_decision": doc.agent_decision,
        "tamper_score": doc.extracted_json.get("tamper_score", 0.0) if doc.extracted_json else 0.0,
        "created_at": getattr(doc, 'created_at', None),
        "file_path": f"/uploads/{doc.filename}" if doc.filename else None
    }

@app.post("/claims/decision")
def agent_update_claim_decision(doc_id: int, decision: str, note: str = "", db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "Document not found"}
    doc.agent_decision = decision
    doc.agent_notes = note
    db.commit()
    return {"success": True, "message": "Decision updated"}

@app.get("/fraud_graph")
def get_fraud_graph(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    all_docs = []
    for d in docs:
        doc_json = dict(d.extracted_json or {})
        doc_json["id"] = d.id
        doc_json["filename"] = d.filename
        all_docs.append(doc_json)
    G = build_fraud_graph(all_docs)
    graph_json = graph_to_json(G)
    return graph_json

@app.get("/shap_explain/{doc_id}")
def shap_explain(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not doc.extracted_json:
        return {"error": "No extracted data for this document."}

    try:
        
        model = joblib.load("eligibility_model.pkl")

        
        trained_features = [
            "claim_amount",
            "tamper_score",
            "policy_active",
            
            "feat_4","feat_5","feat_6","feat_7","feat_8","feat_9","feat_10",
            "feat_11","feat_12","feat_13","feat_14","feat_15","feat_16","feat_17",
            "feat_18","feat_19","feat_20","feat_21","feat_22","feat_23","feat_24",
            "feat_25","feat_26","feat_27","feat_28","feat_29","feat_30","feat_31",
            "feat_32","feat_33","feat_34","feat_35","feat_36","feat_37","feat_38"
        ]

        
        base_features = {
            "claim_amount": doc.extracted_json.get("claim_amount", 0.0),
            "tamper_score": doc.extracted_json.get("tamper_score", 0.0),
            "policy_active": 1 if doc.extracted_json.get("policy_is_active", False) else 0,
        }

        
        features_dict = {name: float(base_features.get(name, 0.0)) for name in trained_features}

        x = pd.DataFrame([features_dict])

        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x, check_additivity=False) 

        
        feature_importance = []
        for idx, feature in enumerate(x.columns):
            
            if isinstance(shap_values, list):
                sv = float(shap_values[0][idx])
            else:
                sv = float(shap_values[0][idx])

            feature_importance.append({
                "feature": feature,
                "value": float(x[feature].iloc[0]),
                "shap_value": sv,
            })

        feature_importance.sort(key=lambda f: abs(f["shap_value"]), reverse=True)

        base_value = explainer.expected_value
        if isinstance(base_value, (list, tuple)):
            base_value = float(base_value[0])
        else:
            base_value = float(base_value)

        return {
            "doc_id": doc_id,
            "features": feature_importance,
            "base_value": base_value,
        }

    except FileNotFoundError:
        return {"error": "Model file 'eligibility_model.pkl' not found. Train and save the model first."}
    except Exception as e:
        return {"error": str(e)}

    
    
    features_dict = {
        'claim_amount': doc.extracted_json.get('claim_amount', 0),
        'tamper_score': doc.extracted_json.get('tamper_score', 0),
        'policy_active': 1 if doc.extracted_json.get('policy_is_active', False) else 0,
        
    }
    
    x = pd.DataFrame([features_dict])
    
    try:
        model = joblib.load("eligibility_model.pkl")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x)
        
        
        feature_importance = []
        for idx, feature in enumerate(x.columns):
            feature_importance.append({
                "feature": feature,
                "value": float(x[feature].iloc[0]),
                "shap_value": float(shap_values[0][idx]) if isinstance(shap_values, list) else float(shap_values[0][idx])
            })
        
        
        feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        
        return {
            "doc_id": doc_id,
            "feature_importance": feature_importance,
            "base_value": float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0
        }
    except FileNotFoundError:
        return {"error": "Model file 'eligibility_model.pkl' not found. Train and save the model first."}
    except Exception as e:
        return {"error": str(e)}

@app.post("/verify_policy")
async def verify_policy(request: VerificationRequest, db: Session = Depends(get_db)):
    
    policy_no_normalized = request.policy_no.upper().strip()
    policy_no_normalized = re.sub(r'\s+', ' ', policy_no_normalized)
    policy_no_normalized = re.sub(r'\s*-\s*', '-', policy_no_normalized)
    
    print(f"\n[DEBUG] Verifying policy number: '{request.policy_no}' → '{policy_no_normalized}'")
    
   
    policy = db.query(MockInsurerPolicy).filter(
        MockInsurerPolicy.policy_number == policy_no_normalized
    ).first()
    
    if not policy:
        print(f"[DEBUG] ❌ Policy NOT FOUND in database")
        print(f"[DEBUG] Available policies in DB:")
        all_policies = db.query(MockInsurerPolicy).all()
        for p in all_policies:
            print(f"  - {p.policy_number}")
        return {"status": "REJECT", "reason": "Policy number not found."}
    
    print(f"[DEBUG] ✓ Policy FOUND: {policy.policy_number}")
    print(f"[DEBUG] Policy Holder: {policy.policy_holder_name}")
    print(f"[DEBUG] Coverage Limit: ${policy.coverage_limit}")
    print(f"[DEBUG] Is Active: {policy.is_active}")
    
    
    name_match_score = fuzz.ratio(request.name.lower(), policy.policy_holder_name.lower())
    print(f"[DEBUG] Name match score: {name_match_score}%")
    
    flags = []
    
    if name_match_score < 80:
        flags.append(f"Name mismatch (Score: {name_match_score:.2f}). DB: '{policy.policy_holder_name}', OCR: '{request.name}'.")
    
    if request.claim_amount > policy.coverage_limit:
        flags.append(f"Claim amount (${request.claim_amount}) exceeds coverage limit (${policy.coverage_limit}).")
    
    if not policy.is_active:
        flags.append("Policy is not active.")
    
    policy_details = {
        "policy_number": policy.policy_number,
        "policy_holder_name": policy.policy_holder_name,
        "coverage_type": policy.coverage_type,
        "coverage_limit": policy.coverage_limit,
        "is_active": policy.is_active
    }
    
    if flags:
        print(f"[DEBUG] ⚠️  MANUAL REVIEW required: {len(flags)} flag(s)")
        return {
            "status": "MANUAL_REVIEW", 
            "reason": "Flags raised", 
            "flags": flags, 
            "policy_details": policy_details
        }
    
    print(f"[DEBUG] ✓ Policy VERIFIED - no issues")
    return {
        "status": "CLEAR", 
        "reason": "Policy verified", 
        "policy_details": policy_details
    }


@app.post("/predict_eligibility")
async def predict_eligibility(request: EligibilityRequest):
    try:
        claim_amount = request.features.get("total_claim_amount", 0)
        prob = 0.85 if claim_amount > 75000 else 0.10
        is_eligible = prob < 0.5
        return {
            "is_eligible": is_eligible,
            "probability_ineligible": prob,
            "explanation": "Mock prediction for demo."
        }
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/fraud_score")
async def fraud_score(request: EligibilityRequest):
    try:
        score = 0.2 if request.features.get("incident_severity") == "Total Loss" else 0.1
        return {"risk_score": score, "is_anomaly": bool(score > 0.75)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/process_full_claim")
async def process_full_claim(request: WorkflowRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == request.doc_id).first()
    if not doc or doc.status != "processed":
        return {"error": "Document not processed yet."}
    
    extracted_data = doc.extracted_json or {}
     
    print(f"\n[DEBUG] ==================== WORKFLOW DEBUG ====================")
    print(f"[DEBUG] Document ID: {request.doc_id}")
    print(f"[DEBUG] Keys in extracted_data: {list(extracted_data.keys())}")
    print(f"[DEBUG] duplicate_check present: {'duplicate_check' in extracted_data}")
    if 'duplicate_check' in extracted_data:
        print(f"[DEBUG] duplicate_check contents: {extracted_data['duplicate_check']}")
    print(f"[DEBUG] ========================================================\n")
          
    
    duplicate_check = extracted_data.get("duplicate_check", {})
    if duplicate_check.get("is_duplicate"):
        return {
            "decision": "REJECT_DUPLICATE",
            "reason": f"Duplicate claim detected. This document matches {duplicate_check['duplicate_count']} existing claim(s).",
            "duplicate_details": duplicate_check.get("similar_docs", []),
            "all_data": {
                "ocr": extracted_data,
                "duplicate_check": duplicate_check
            }
        }

    
    verify_req = VerificationRequest(
        policy_no=extracted_data.get("policy_no", "UNKNOWN"),
        name=extracted_data.get("name", "UNKNOWN"),
        claim_amount=request.claim_amount
    )
    verify_response = await verify_policy(verify_req, db)

    
    mock_features = {
        "total_claim_amount": request.claim_amount,
        "incident_severity": "Total Loss" if request.claim_amount > 75000 else "Minor Damage",
    }
    eligibility_req = EligibilityRequest(features=mock_features)
    eligibility_response = await predict_eligibility(eligibility_req)

    
    fraud_response = await fraud_score(eligibility_req)

    
    facts = {
        "policy_no": extracted_data.get("policy_no", "UNKNOWN"),
        "verification_status": verify_response.get("status"),
        "verification_reason": verify_response.get("reason"),
        "policy_is_active": verify_response.get("policy_details", {}).get("is_active", False),
        "is_eligible": eligibility_response.get("is_eligible"),
        "ineligible_prob": eligibility_response.get("probability_ineligible"),
        "fraud_risk_score": fraud_response.get("risk_score"),
        "has_duplicates": duplicate_check.get("is_duplicate", False),  # ADD THIS
        "decision": None
    }
    
    print("⚙️ Executing Rule Engine for:", facts)
    
    try:
        result_state = post_to_ruleset('insurance_workflow', facts)

        if not result_state or 'decision' not in result_state:
            raise Exception("Rule engine executed but failed to set a 'decision' state.")

        final_decision = {
            "decision": result_state.get("decision", "ERROR"),
            "reason": result_state.get("reason", "Rule engine did not reach a final decision."),
            "all_data": {
                "ocr": extracted_data,
                "verification": verify_response,
                "eligibility": eligibility_response,
                "fraud": fraud_response,
                "duplicate_check": duplicate_check,  
                "combined_facts": facts
            }
        }
        
        doc.status = f"workflow_complete: {final_decision['decision']}"
        db.commit()
        return final_decision
        
    except Exception as e:
        print(f"Rule engine failed with exception: {e}")
        return {
            "error": f"Rule engine failed: {str(e)}", 
            "reason": "Internal Rule Engine Failure. Check server logs.", 
            "facts_sent": facts
        }
@app.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    hashed = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"username": new_user.username, "email": new_user.email, "role": new_user.role}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        
        user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
   
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,  
        "email": user.email,
        "username": user.username
    }


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@app.get("/protected-example")
def protected_example(user: dict = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}, you are authenticated!"}

from fastapi.responses import FileResponse

@app.get("/view_document/{doc_id}")
def view_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "Document not found"}
    
    
    filename = os.path.basename(doc.local_path)
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, doc.filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "File not found on disk"}

    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
