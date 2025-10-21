# import os
# import shutil
# import uvicorn
# import json
# import joblib
# import pandas as pd
# from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, JSON, Boolean
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.ext.declarative import declarative_base
# from rapidfuzz import fuzz
# from durable.lang import post as post_to_ruleset

# # --- Local Imports (Must be after app/db setup if they import from main) ---
# from rules import insurance_workflow

# # --- Database Setup (SQLite) ---
# DATABASE_URL = "sqlite:///./project.db"
# Base = declarative_base()
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # --- File Storage Setup ---
# UPLOAD_DIR = "./uploaded_files"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # --- FastAPI App Instantiation ---
# app = FastAPI()

# # --- SQLAlchemy Database Models ---

# class Document(Base):
#     __tablename__ = "documents"
#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String, index=True)
#     local_path = Column(String)
#     status = Column(String, default="pending_ocr") # e.g., pending_ocr, processed, failed
#     extracted_json = Column(JSON, nullable=True)

# class MockInsurerPolicy(Base):
#     __tablename__ = "mock_insurer_db"
#     id = Column(Integer, primary_key=True, index=True)
#     policy_number = Column(String, unique=True, index=True)
#     policy_holder_name = Column(String)
#     coverage_type = Column(String)
#     coverage_limit = Column(Integer)
#     is_active = Column(Boolean, default=True)

# # --- Create All Database Tables ---
# Base.metadata.create_all(bind=engine) 

# # --- Pydantic Request/Response Models ---

# class VerificationRequest(BaseModel):
#     policy_no: str
#     name: str
#     claim_amount: float

# class EligibilityRequest(BaseModel):
#     features: dict

# class WorkflowRequest(BaseModel):
#     doc_id: int
#     claim_amount: float # User enters this manually in the demo

# # --- Load ML Models on Startup ---

# try:
#     eligibility_model = joblib.load("eligibility_model.pkl")
#     fraud_model = joblib.load("fraud_model.pkl")
#     print("ML models loaded successfully.")
# except FileNotFoundError:
#     print("WARNING: ML models (eligibility_model.pkl, fraud_model.pkl) not found.")
#     print("WARNING: Please run the training notebook to create them.")
#     eligibility_model = None
#     fraud_model = None

# # --- CORS Middleware ---
# # Allows all origins ("*") for local development
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Dependencies ---

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # We need to import this *after* the db models are defined
# from ocr_module import process_document 

# # --- API Endpoints ---

# @app.post("/upload")
# async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     db = SessionLocal()
    
#     # 1. Save file to local disk (our "S3")
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
        
#     # 2. Insert metadata into RDS (our "SQLite")
#     new_doc = Document(
#         filename=file.filename,
#         local_path=file_path,
#         status="pending_ocr"
#     )
#     db.add(new_doc)
#     db.commit()
#     db.refresh(new_doc)
    
#     # 3. Trigger async OCR task (our "SQS/Lambda")
#     background_tasks.add_task(process_document, doc_id=new_doc.id, file_path=file_path)
    
#     db.close()
    
#     return {"message": f"File '{file.filename}' uploaded. OCR started.", "doc_id": new_doc.id}

# @app.get("/status/{doc_id}")
# async def get_status(doc_id: int, db: Session = Depends(get_db)):
#     doc = db.query(Document).filter(Document.id == doc_id).first()
#     if not doc:
#         return {"error": "Document not found"}
#     return {"id": doc.id, "filename": doc.filename, "status": doc.status, "data": doc.extracted_json}

# @app.post("/verify_policy")
# async def verify_policy(request: VerificationRequest, db: Session = Depends(get_db)):
#     # 1. Query insurer DB API (our mock DB)
#     policy = db.query(MockInsurerPolicy).filter(MockInsurerPolicy.policy_number == request.policy_no).first()
    
#     if not policy:
#         return {"status": "REJECT", "reason": "Policy number not found."}

#     # 2. Fuzzy match name
#     name_match_score = fuzz.ratio(request.name.lower(), policy.policy_holder_name.lower())
    
#     flags = []
#     if name_match_score < 80:
#         flags.append(f"Name mismatch (Score: {name_match_score:.2f}). Found '{policy.policy_holder_name}', got '{request.name}'.")
        
#     # 3. Rule: Check coverage
#     if request.claim_amount > policy.coverage_limit:
#         flags.append(f"Claim amount (${request.claim_amount}) exceeds coverage limit (${policy.coverage_limit}).")

#     if not policy.is_active:
#         flags.append("Policy is not active.")

#     if flags:
#         # Manually create dict to avoid SQLAlchemy state issues
#         policy_details = {
#             "policy_number": policy.policy_number,
#             "policy_holder_name": policy.policy_holder_name,
#             "coverage_limit": policy.coverage_limit,
#             "is_active": policy.is_active
#         }
#         return {"status": "MANUAL_REVIEW", "reason": "Flags raised.", "flags": flags, "policy_details": policy_details}
        
#     policy_details = {
#         "policy_number": policy.policy_number,
#         "policy_holder_name": policy.policy_holder_name,
#         "coverage_limit": policy.coverage_limit,
#         "is_active": policy.is_active
#     }
#     return {"status": "CLEAR", "reason": "Policy verified.", "policy_details": policy_details}

# @app.post("/predict_eligibility")
# async def predict_eligibility(request: EligibilityRequest):
#     # Convert incoming dict to a DataFrame in the correct order
#     try:
#         # Simplified prediction for demo:
#         # We can't easily re-run the LabelEncoder here, so we'll mock
#         # a "high risk" score based on claim amount
#         if request.features.get("total_claim_amount", 0) > 75000:
#              prob = 0.85 # High chance of fraud (ineligible)
#         else:
#              prob = 0.10 # Low chance
        
#         # Real logic would use the loaded model:
#         # if eligibility_model:
#         #     df = pd.DataFrame([request.features])
#         #     # ... apply real preprocessing ...
#         #     prediction = eligibility_model.predict(df)
#         #     prob = prediction[0]
        
#         is_eligible = bool(prob < 0.5) # Threshold
        
#         return {
#             "is_eligible": is_eligible,
#             "probability_ineligible": prob,
#             "explanation": "SHAP summary would go here." # Module 4: SHAP
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.post("/fraud_score")
# async def fraud_score(request: EligibilityRequest): # Re-use the same Pydantic model
#     try:
#         # Mock logic:
#         score = 0.1 # Normal
#         if request.features.get("incident_severity") == "Total Loss":
#             score = 0.9 # High risk
        
#         # Real logic would use the loaded model:
#         # if fraud_model:
#         #     df = pd.DataFrame([request.features])
#         #     # ... apply real preprocessing ...
#         #     prediction = fraud_model.predict(df) # Returns 1 for inlier, -1 for outlier
#         #     score = 1 if prediction[0] == -1 else 0

#         return {
#             "risk_score": score, # 0-1 scale
#             "is_anomaly": bool(score > 0.75)
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.post("/process_full_claim")
# async def process_full_claim(request: WorkflowRequest, db: Session = Depends(get_db)):
#     # 1. Get OCR'd data from DB
#     doc = db.query(Document).filter(Document.id == request.doc_id).first()
#     if not doc or doc.status != "processed":
#         return {"error": "Document not processed or not found."}
    
#     extracted_data = doc.extracted_json
    
#     # --- This is your "Step Function" ---
    
#     # Step 1: Call Identity Matching
#     verify_req = VerificationRequest(
#         policy_no=extracted_data.get("policy_no") or "UNKNOWN",  # FIX
#         name=extracted_data.get("name") or "UNKNOWN",        # FIX
#         claim_amount=request.claim_amount
#     )
#     verify_response = await verify_policy(verify_req, db)

#     # Step 2: Call Eligibility Prediction
#     mock_features = {
#         "total_claim_amount": request.claim_amount,
#         "incident_severity": "Total Loss" if request.claim_amount > 75000 else "Minor Damage",
#         # ... add other features known from OCR
#     }
#     eligibility_req = EligibilityRequest(features=mock_features)
#     eligibility_response = await predict_eligibility(eligibility_req)
    
#     # Step 3: Call Fraud Detection
#     fraud_response = await fraud_score(eligibility_req)
    
#     # --- Step 4: Combine in Rule Engine ---
#     facts = {
#         "policy_no": extracted_data.get("policy_no", "UNKNOWN"),
#         "verification_status": verify_response.get("status"),
#         "verification_reason": verify_response.get("reason"),
#         "policy_is_active": verify_response.get("policy_details", {}).get("is_active", False),
#         "is_eligible": eligibility_response.get("is_eligible"),
#         "ineligible_prob": eligibility_response.get("probability_ineligible"),
#         "fraud_risk_score": fraud_response.get("risk_score")
#     }
#     print("!!!!!!!!!! EXECUTING THE NEW, FIXED CODE. QUOTES ARE HERE. !!!!!!!!!!!")
#     try:
#         # Run the durable_rules engine
#         result_state = post_to_ruleset("insurance_workflow", facts) # FIX
        
#         final_decision = {
#             "decision": result_state.get("decision", "ERROR"),
#             "reason": result_state.get("reason", "Rule engine failed."),
#             "all_data": {
#                 "ocr": extracted_data,
#                 "verification": verify_response, # This is already a clean dict
#                 "eligibility": eligibility_response,
#                 "fraud": fraud_response,
#                 "combined_facts": facts
#             }
#         }
        
#         # Log decision
#         doc.status = f"workflow_complete: {final_decision['decision']}"
#         db.commit()
        
#         return final_decision
        
#     except Exception as e:
#         return {"error": f"Rule engine failed: {str(e)}"}

# # --- Main Entry Point ---

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# main.py
# import os
# import shutil
# import uvicorn
# import json
# import joblib
# import pandas as pd
# from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, JSON, Boolean
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.ext.declarative import declarative_base
# from rapidfuzz import fuzz
# from durable.lang import post  # ✅ Correct import for posting facts

# # --- Import your ruleset after defining app/db ---
# from rules import * # this ensures ruleset is registered

# # --- Database Setup ---
# DATABASE_URL = "sqlite:///./project.db"
# Base = declarative_base()
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # --- File Upload Setup ---
# UPLOAD_DIR = "./uploaded_files"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # --- FastAPI App ---
# app = FastAPI()

# # --- Database Models ---
# class Document(Base):
#     __tablename__ = "documents"
#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String, index=True)
#     local_path = Column(String)
#     status = Column(String, default="pending_ocr")
#     extracted_json = Column(JSON, nullable=True)

# class MockInsurerPolicy(Base):
#     __tablename__ = "mock_insurer_db"
#     id = Column(Integer, primary_key=True, index=True)
#     policy_number = Column(String, unique=True, index=True)
#     policy_holder_name = Column(String)
#     coverage_type = Column(String)
#     coverage_limit = Column(Integer)
#     is_active = Column(Boolean, default=True)

# Base.metadata.create_all(bind=engine)

# # --- Pydantic Models ---
# class VerificationRequest(BaseModel):
#     policy_no: str
#     name: str
#     claim_amount: float

# class EligibilityRequest(BaseModel):
#     features: dict

# class WorkflowRequest(BaseModel):
#     doc_id: int
#     claim_amount: float

# # --- Load ML Models (if available) ---
# try:
#     eligibility_model = joblib.load("eligibility_model.pkl")
#     fraud_model = joblib.load("fraud_model.pkl")
#     print("✅ ML models loaded successfully.")
# except FileNotFoundError:
#     print("⚠️ ML models not found — using mock predictions.")
#     eligibility_model = None
#     fraud_model = None

# # --- CORS ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- DB Dependency ---
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Import OCR function
# from ocr_module import process_document


# # ---------------- API Endpoints ---------------- #

# @app.post("/upload")
# async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     db = SessionLocal()
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     new_doc = Document(filename=file.filename, local_path=file_path, status="pending_ocr")
#     db.add(new_doc)
#     db.commit()
#     db.refresh(new_doc)

#     background_tasks.add_task(process_document, doc_id=new_doc.id, file_path=file_path)
#     db.close()
#     return {"message": f"File '{file.filename}' uploaded and OCR started.", "doc_id": new_doc.id}


# @app.get("/status/{doc_id}")
# async def get_status(doc_id: int, db: Session = Depends(get_db)):
#     doc = db.query(Document).filter(Document.id == doc_id).first()
#     if not doc:
#         return {"error": "Document not found"}
#     return {"id": doc.id, "filename": doc.filename, "status": doc.status, "data": doc.extracted_json}


# @app.post("/verify_policy")
# async def verify_policy(request: VerificationRequest, db: Session = Depends(get_db)):
#     search_string = f"%{request.policy_no}%"
#     policy = db.query(MockInsurerPolicy).filter(MockInsurerPolicy.policy_number.like(search_string)).first()

#     if not policy:
#         return {"status": "REJECT", "reason": "Policy number not found."}

#     name_match_score = fuzz.ratio(request.name.lower(), policy.policy_holder_name.lower())
#     flags = []

#     if name_match_score < 80:
#         flags.append(f"Name mismatch (Score: {name_match_score:.2f}).")

#     if request.claim_amount > policy.coverage_limit:
#         flags.append(f"Claim exceeds coverage limit (${policy.coverage_limit}).")

#     if not policy.is_active:
#         flags.append("Policy is not active.")

#     policy_details = {
#         "policy_number": policy.policy_number,
#         "policy_holder_name": policy.policy_holder_name,
#         "coverage_type": policy.coverage_type,
#         "coverage_limit": policy.coverage_limit,
#         "is_active": policy.is_active
#     }

#     if flags:
#         return {"status": "MANUAL_REVIEW", "reason": "Flags raised", "flags": flags, "policy_details": policy_details}

#     return {"status": "CLEAR", "reason": "Policy verified", "policy_details": policy_details}


# @app.post("/predict_eligibility")
# async def predict_eligibility(request: EligibilityRequest):
#     try:
#         claim_amount = request.features.get("total_claim_amount", 0)
#         prob = 0.85 if claim_amount > 75000 else 0.10
#         is_eligible = prob < 0.5
#         return {
#             "is_eligible": is_eligible,
#             "probability_ineligible": prob,
#             "explanation": "Mock prediction for demo."
#         }
#     except Exception as e:
#         return {"error": str(e)}


# @app.post("/fraud_score")
# async def fraud_score(request: EligibilityRequest):
#     try:
#         score = 0.9 if request.features.get("incident_severity") == "Total Loss" else 0.1
#         return {"risk_score": score, "is_anomaly": bool(score > 0.75)}
#     except Exception as e:
#         return {"error": str(e)}


# @app.post("/process_full_claim")
# async def process_full_claim(request: WorkflowRequest, db: Session = Depends(get_db)):
#     doc = db.query(Document).filter(Document.id == request.doc_id).first()
#     if not doc or doc.status != "processed":
#         return {"error": "Document not processed or not found."}

#     extracted_data = doc.extracted_json or {}

#     # Step 1: Verify Policy
#     verify_req = VerificationRequest(
#         policy_no=extracted_data.get("policy_no") or "UNKNOWN",
#         name=extracted_data.get("name") or "UNKNOWN",
#         claim_amount=request.claim_amount
#     )
#     verify_response = await verify_policy(verify_req, db)

#     # Step 2: Eligibility
#     mock_features = {
#         "total_claim_amount": request.claim_amount,
#         "incident_severity": "Total Loss" if request.claim_amount > 75000 else "Minor Damage",
#     }
#     eligibility_req = EligibilityRequest(features=mock_features)
#     eligibility_response = await predict_eligibility(eligibility_req)

#     # Step 3: Fraud Detection
#     fraud_response = await fraud_score(eligibility_req)

#     # Step 4: Combine facts for rule engine
#     facts = {
#         "policy_no": extracted_data.get("policy_no", "UNKNOWN"),
#         "verification_status": verify_response.get("status"),
#         "verification_reason": verify_response.get("reason"),
#         "policy_is_active": verify_response.get("policy_details", {}).get("is_active", False),
#         "is_eligible": eligibility_response.get("is_eligible"),
#         "ineligible_prob": eligibility_response.get("probability_ineligible"),
#         "fraud_risk_score": fraud_response.get("risk_score")
#     }

#     print("⚙️ Executing Rule Engine for:", facts)

#     try:
#         # --- FIX IS HERE ---
#         # 1. Capture the result from post()
#         result_state = post('insurance_workflow', facts)

#         # 2. Use the result_state to get the decision
#         final_decision = {
#             "decision": result_state.get("decision", "ERROR"),
#             "reason": result_state.get("reason", "Rule engine did not provide a reason."),
#             "all_data": {
#                 "ocr": extracted_data,
#                 "verification": verify_response,
#                 "eligibility": eligibility_response,
#                 "fraud": fraud_response,
#                 "combined_facts": facts
#             }
#         }
#         # --- END OF FIX ---

#         doc.status = f"workflow_complete: {final_decision['decision']}"
#         db.commit()
        
#         return final_decision

#     except Exception as e:
#         # This will catch errors like "Ruleset not found"
#         print(f"Rule engine failed with exception: {e}")
#         return {"error": f"Rule engine failed: {str(e)}"}


# # --- Main Entry Point ---
# if __name__ == "__main__": # <-- Also fixed a syntax error here (was missing colon)
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
import os
import shutil
import uvicorn
import json
import joblib
import pandas as pd
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON, Boolean
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from rapidfuzz import fuzz
from durable.lang import post as post_to_ruleset

# --- Import your ruleset after defining app/db ---
# Note: Ruleset registration can be tricky with reload.
# If "Ruleset not found" errors persist, move this import inside process_full_claim.
from rules import * # --- Database Setup ---
DATABASE_URL = "sqlite:///./project.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- File Upload Setup ---
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- FastAPI App ---
app = FastAPI()

# --- Database Models ---
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    local_path = Column(String)
    status = Column(String, default="pending_ocr")
    extracted_json = Column(JSON, nullable=True)

class MockInsurerPolicy(Base):
    __tablename__ = "mock_insurer_db"
    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String, unique=True, index=True)
    policy_holder_name = Column(String)
    coverage_type = Column(String)
    coverage_limit = Column(Integer)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# --- Pydantic Models ---
class VerificationRequest(BaseModel):
    policy_no: str
    name: str
    claim_amount: float

class EligibilityRequest(BaseModel):
    features: dict

class WorkflowRequest(BaseModel):
    doc_id: int
    claim_amount: float

# --- Load ML Models (if available) ---
try:
    eligibility_model = joblib.load("eligibility_model.pkl")
    fraud_model = joblib.load("fraud_model.pkl")
    print("✅ ML models loaded successfully.")
except FileNotFoundError:
    print("⚠️ ML models not found — using mock predictions.")
    eligibility_model = None
    fraud_model = None

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import OCR function
from ocr_module import process_document


# ---------------- API Endpoints ---------------- #

@app.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    db = SessionLocal()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(filename=file.filename, local_path=file_path, status="pending_ocr")
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    background_tasks.add_task(process_document, doc_id=new_doc.id, file_path=file_path)
    db.close()
    return {"message": f"File '{file.filename}' uploaded and OCR started.", "doc_id": new_doc.id}


@app.get("/status/{doc_id}")
async def get_status(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "Document not found"}
    return {"id": doc.id, "filename": doc.filename, "status": doc.status, "data": doc.extracted_json}


@app.post("/verify_policy")
async def verify_policy(request: VerificationRequest, db: Session = Depends(get_db)):
    
    # --- START DEBUG LOGGING ---
    print("\n--- DEBUG: Inside verify_policy ---")
    print(f"Received policy_no: '{request.policy_no}' (Type: {type(request.policy_no)}, Length: {len(request.policy_no)})")
    # Optional: Print character codes to reveal hidden chars
    # print(f"Char codes: {[ord(c) for c in request.policy_no]}") 
    
    # Use LIKE search, ensure request.policy_no is not None or empty
    search_term = request.policy_no if request.policy_no else "INVALID_SEARCH_TERM"
    search_string = f"%{search_term}%" 
    print(f"Database search string: '{search_string}'")
    # --- END DEBUG LOGGING ---

    # Query insurer DB API (our mock DB)
    policy = db.query(MockInsurerPolicy).filter(MockInsurerPolicy.policy_number.like(search_string)).first()
    
    # --- MORE DEBUG LOGGING ---
    if policy:
        print(f"Database FOUND policy_no: '{policy.policy_number}' (Type: {type(policy.policy_number)}, Length: {len(policy.policy_number)})")
        # print(f"DB Char codes: {[ord(c) for c in policy.policy_number]}")
    else:
        print("Database did NOT find a matching policy using LIKE search.")
        # Let's see what IS in the database
        all_policies = db.query(MockInsurerPolicy.policy_number).all()
        print(f"Policy numbers currently in DB: {[p[0] for p in all_policies]}")
    print("--- END DEBUG ---\n")
    # --- END MORE DEBUG LOGGING ---
    
    if not policy:
        return {"status": "REJECT", "reason": "Policy number not found."}

    # Fuzzy match name
    name_match_score = fuzz.ratio((request.name or "").lower(), (policy.policy_holder_name or "").lower())
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
        return {"status": "MANUAL_REVIEW", "reason": "Flags raised", "flags": flags, "policy_details": policy_details}

    return {"status": "CLEAR", "reason": "Policy verified", "policy_details": policy_details}


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
        score = 0.9 if request.features.get("incident_severity") == "Total Loss" else 0.1
        return {"risk_score": score, "is_anomaly": bool(score > 0.75)}
    except Exception as e:
        return {"error": str(e)}


@app.post("/process_full_claim")
async def process_full_claim(request: WorkflowRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == request.doc_id).first()
    if not doc or doc.status not in ["processed", "failed_ocr"]: # Allow processing even if OCR had issues
        return {"error": f"Document not processed or not found (Status: {getattr(doc, 'status', 'Not Found')})."}

    extracted_data = doc.extracted_json or {}
    
    # Handle case where AI returned an error object
    if "error" in extracted_data and doc.status == "failed_ocr":
        print(f"Workflow stopped early for doc_id {request.doc_id} due to OCR error: {extracted_data['error']}")
        # Decide how to handle OCR failures - maybe manual review?
        return {
            "decision": "MANUAL_REVIEW", 
            "reason": f"OCR failed or document type unknown: {extracted_data.get('error', 'Unknown OCR issue')}",
            "all_data": {"ocr": extracted_data}
        }
    elif "error" in extracted_data: # Should ideally not happen if status is 'processed'
        print(f"WARNING: Processed doc {request.doc_id} has error in JSON: {extracted_data['error']}")
        # Fallback - treat as if OCR failed
        extracted_data = {} 


    # Step 1: Verify Policy
    verify_req = VerificationRequest(
        # Use .get() with default to handle missing keys gracefully
        policy_no=extracted_data.get("policy_no", "UNKNOWN"), 
        name=extracted_data.get("name", "UNKNOWN"),
        claim_amount=request.claim_amount
    )
    verify_response = await verify_policy(verify_req, db)

    # Step 2: Eligibility
    mock_features = {
        "total_claim_amount": request.claim_amount,
        "incident_severity": "Total Loss" if request.claim_amount > 75000 else "Minor Damage",
    }
    eligibility_req = EligibilityRequest(features=mock_features)
    eligibility_response = await predict_eligibility(eligibility_req)

    # Step 3: Fraud Detection
    fraud_response = await fraud_score(eligibility_req)

    # Step 4: Combine facts for rule engine
    facts = {
        "policy_no": extracted_data.get("policy_no", "UNKNOWN"),
        "verification_status": verify_response.get("status"),
        "verification_reason": verify_response.get("reason"),
        "policy_is_active": verify_response.get("policy_details", {}).get("is_active", False),
        "is_eligible": eligibility_response.get("is_eligible"),
        "ineligible_prob": eligibility_response.get("probability_ineligible"),
        "fraud_risk_score": fraud_response.get("risk_score")
    }

    print("⚙️ Executing Rule Engine for:", facts)

    try:
        # 1. Import post and get_state here
        from durable.lang import post, get_state, delete_state

        # --- Clear previous state (important for retries) ---
        try:
            delete_state('insurance_workflow')
            print("DEBUG: Cleared previous rule engine state.")
        except Exception as e:
            # Ignore if state didn't exist
            # print(f"DEBUG: Could not clear state (may not exist yet): {e}")
            pass

        # 2. Post the facts to the ruleset
        print(f"DEBUG: Posting facts to ruleset: {facts}")
        post('insurance_workflow', facts) 

        # 3. Get the resulting state 
        result_state = get_state('insurance_workflow') 
        print(f"DEBUG: Raw result_state from get_state(): {result_state}")

        # --- Check if rules actually produced a decision ---
        if not result_state or 'decision' not in result_state:
             print("ERROR: Rule engine did not produce a decision.")
             # Provide a default decision if none was made (e.g., manual review)
             final_decision = {
                 "decision": "MANUAL_REVIEW", 
                 "reason": "Rule engine did not reach a final decision based on the facts provided.",
                 "all_data": {
                     "ocr": extracted_data,
                     "verification": verify_response,
                     "eligibility": eligibility_response,
                     "fraud": fraud_response,
                     "combined_facts": facts
                 }
             }
        else:
            # 4. Build the final decision using the retrieved state
            final_decision = {
                "decision": result_state.get("decision", "ERROR_UNEXPECTED"), # Should have 'decision' now
                "reason": result_state.get("reason", "Rule engine provided no reason."),
                "all_data": {
                    "ocr": extracted_data,
                    "verification": verify_response,
                    "eligibility": eligibility_response,
                    "fraud": fraud_response,
                    "combined_facts": facts 
                }
            }
        # --- END OF FIX ---

        doc.status = f"workflow_complete: {final_decision['decision']}"
        db.commit()

        return final_decision

    except Exception as e:
        # This will catch errors like "Ruleset not found" etc.
        print(f"Rule engine failed with exception: {e}")
        return {"error": f"Rule engine failed: {str(e)}", "facts_sent": facts}

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)