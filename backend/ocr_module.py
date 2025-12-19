import pytesseract
import spacy
import re
from pdf2image import convert_from_path
from PIL import Image
import imagehash
import os
import sys

from models import Document
from db import engine, SessionLocal

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_bin_path = r"C:\Users\Karunya Paul\Downloads\Release-24.02.0-0\poppler-24.02.0\Library\bin"

nlp = spacy.load("en_core_web_sm")
processor = None
model = None
layoutlm_available = False

try:
    from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
    import torch
    
    print("Loading LayoutLMv3 models...")
    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")
    model.eval()  
    layoutlm_available = True
    print("✓ LayoutLMv3 models loaded successfully.")
    
except ImportError as e:
    print(f"Warning: transformers library not installed. LayoutLM will be skipped. Error: {e}")
    layoutlm_available = False
    
except Exception as e:
    print(f"Warning: LayoutLMv3 models could not be loaded. Layout extraction will be skipped. Error: {e}")
    layoutlm_available = False


def clean_policy_no(raw_policy_no):
   
    if not raw_policy_no:
        return None

    
    cleaned = re.sub(r'[^A-Z0-9 \-]+', '', str(raw_policy_no), flags=re.IGNORECASE)
    
    
    cleaned = cleaned.upper().strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)  
    cleaned = re.sub(r'\s*-\s*', '-', cleaned)  
    
    print(f"[DEBUG] Policy number cleaned: '{raw_policy_no}' → '{cleaned}'")
    return cleaned


def extract_home_data(text):
    
    entities = {"policy_type": "Home"}
    
    
    match = re.search(r"HOMEOWNERS POLICY NO\.?\s*:?\s*([A-Z0-9 \-]+)", text, re.IGNORECASE)
    if match: 
        entities["policy_no"] = clean_policy_no(match.group(1))
        print(f"[DEBUG] Home policy found: {entities['policy_no']}")

  
    match = re.search(r"(John A\. Smith and Jane B\. Smith)", text, re.IGNORECASE)
    if match: 
        entities["name"] = match.group(1).strip()
        
    
    match = re.search(r"E\.\s*Personal Liability\s.*?\$([\d,]+)\s+Each Occurrence", text, re.IGNORECASE | re.DOTALL)
    if match: 
        entities["liability_limit"] = match.group(1).replace(",", "")
    
    
    match_from = re.search(r"From:\s+([^\n]+)", text, re.IGNORECASE)
    match_to = re.search(r"To:\s+([^\n]+)", text, re.IGNORECASE)
    if match_from: entities["effective_date"] = match_from.group(1).strip()
    if match_to: entities["expiration_date"] = match_to.group(1).strip()
        
    return entities


def extract_auto_data(text):
    
    entities = {"policy_type": "Auto"}
    match = re.search(r"(?:PERSONAL\s+)?AUTO POLICY NO\.?\s*:?\s*([A-Z0-9 \-]+)", text, re.IGNORECASE)
    if match: 
        entities["policy_no"] = clean_policy_no(match.group(1))
        print(f"[DEBUG] Auto policy found: {entities['policy_no']}")


    match = re.search(r"NAMED INSURED\s+([^\n]+)", text, re.IGNORECASE)
    if match: 
        entities["name"] = match.group(1).strip()
 
    
    match = re.search(r"Bodily Injury\s.*?\$([\d,]+)\s*(?:each\s+)?(?:person|accident)", text, re.IGNORECASE | re.DOTALL)
    if match: 
        entities["liability_limit"] = match.group(1).replace(",", "")
    
    entities["effective_date"] = None
    entities["expiration_date"] = None

    return entities


def extract_umbrella_data(text):
    
    entities = {"policy_type": "Umbrella"}
    
    
    match = re.search(r"(?:PERSONAL\s+)?UMBRELLA(?:\s+LIABILITY)?\s+POLICY NO\.?\s*:?\s*([A-Z0-9 \-]+)", text, re.IGNORECASE)
    if match: 
        entities["policy_no"] = clean_policy_no(match.group(1))
        print(f"[DEBUG] Umbrella policy found: {entities['policy_no']}")

   
    match = re.search(r"NAMED INSURED(?:\s+AND\s+ADDRESS)?\s*\n\s*([^\n]+)", text, re.IGNORECASE)
    if match: 
        entities["name"] = match.group(1).strip()
        
   
    match = re.search(r"LIABILITY COVERAGE:\s+\$([\d,]+)", text, re.IGNORECASE)
    if match: 
        entities["liability_limit"] = match.group(1).replace(",", "")
        
    
    match_from = re.search(r"From:\s+([^\n]+)", text, re.IGNORECASE)
    match_to = re.search(r"To:\s+([^\n]+)", text, re.IGNORECASE)
    if match_from: entities["effective_date"] = match_from.group(1).strip()
    if match_to: entities["expiration_date"] = match_to.group(1).strip()

    return entities


def tamper_score_image(img_path):
   
    try:
        img = Image.open(img_path).convert("RGB")
        hash_orig = imagehash.average_hash(img)
        
        tmp_path = "tmp_ela.jpg"
        img.save(tmp_path, "JPEG", quality=65)
        img_ela = Image.open(tmp_path)
        hash_ela = imagehash.average_hash(img_ela)
        
        score = hash_orig - hash_ela
        os.remove(tmp_path)
        
        return float(score)
    except Exception as e:
        print(f"[ERROR] Tamper score calculation failed: {e}")
        return 0.0


def extract_layout_entities(image_pil, ocr_text=None):
   
    if not layoutlm_available or not processor or not model:
        return {"warning": "LayoutLMv3 models not available"}
    
    try:
       
        if image_pil.mode != "RGB":
            image_pil = image_pil.convert("RGB")
        
        
        encoding = processor(
            image_pil, 
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512
            
        )
        
       
        with torch.no_grad():
            outputs = model(**encoding)
        
        
        predictions = outputs.logits.argmax(-1).squeeze().tolist()
        
        return {
            "status": "success",
            "num_tokens": len(predictions) if isinstance(predictions, list) else 1,
            "note": "LayoutLMv3 inference completed (untrained base model)"
        }
        
    except Exception as e:
        print(f"[ERROR] LayoutLM extraction failed: {e}")
        return {"warning": f"LayoutLM skipped: {str(e)}"} 



def extract_entities_with_spacy(text):
   
    try:
        doc = nlp(text)
        
        ents = {}
        for ent in doc.ents:
            ents[ent.label_] = ent.text
        return ents
    except Exception as e:
        print(f"[ERROR] spaCy entity extraction failed: {e}")
        return {}


def extract_structured_data(pdf_path):
  
    print(f"\n[INFO] Processing document: {pdf_path}")
    
    
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_bin_path)
        print(f"[INFO] Converted PDF to {len(images)} page(s)")
    except Exception as e:
        error_msg = f"PDF conversion failed (check Poppler installation): {e}"
        print(f"[ERROR] {error_msg}")
        return {"error": error_msg}

    
    full_text = ""
    page_images = []
    
    for i, img in enumerate(images):
        print(f"[INFO] Processing page {i+1}/{len(images)}...")
        page_text = pytesseract.image_to_string(img)
        full_text += page_text + "\n"
        tmp_img_path = f"tmp_doc_image_page_{i}.jpg"
        img.save(tmp_img_path, "JPEG", quality=95)
        page_images.append(tmp_img_path)

    print(f"[INFO] OCR completed. Extracted {len(full_text)} characters")

   
    entities = {"company_name": None}
    if "AMICA MUTUAL" in full_text.upper():
        entities["company_name"] = "Amica Mutual Insurance Company"
        print("[INFO] Detected company: Amica Mutual Insurance Company")

    
    policy_types = {
        "PERSONAL AUTO POLICY": extract_auto_data,
        "HOMEOWNERS POLICY": extract_home_data,
        "PERSONAL UMBRELLA": extract_umbrella_data,
    }
    
    doc_data = {}
    for policy_keyword, parser in policy_types.items():
        if policy_keyword in full_text:
            print(f"[INFO] Detected policy type: {policy_keyword}")
            doc_data = parser(full_text)
            break
    
    if not doc_data:
        doc_data = {"note": "Unknown document type"}
        print("[WARNING] Could not determine policy type")

    entities.update(doc_data)
    entities["ocr_text"] = full_text

    
    print("[INFO] Running spaCy NER...")
    entities["spacy_entities"] = extract_entities_with_spacy(full_text)

    
    print("[INFO] Running LayoutLMv3 extraction...")
    try:
        if page_images and layoutlm_available:
            first_page_img = Image.open(page_images[0])
            entities["layout_entities"] = extract_layout_entities(first_page_img, full_text)
        else:
            entities["layout_entities"] = {"warning": "No images or LayoutLM unavailable"}
    except Exception as e:
        print(f"[ERROR] LayoutLM extraction error: {e}")
        entities["layout_entities"] = {"error": str(e)}

    
    print("[INFO] Running tamper detection...")
    try:
        if page_images:
            entities["tamper_score"] = tamper_score_image(page_images[0])
            print(f"[INFO] Tamper score: {entities['tamper_score']}")
    except Exception as e:
        print(f"[ERROR] Tamper detection failed: {e}")
        entities["tamper_score"] = f"Error: {e}"

    
    for path in page_images:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"[WARNING] Could not delete temp file {path}: {e}")

    print("[INFO] ✓ Document processing complete\n")
    return entities


def save_text_file(text, output_dir, doc_id=None):
    
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"doc_{doc_id}.txt" if doc_id else "output.txt"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        print(f"[INFO] ✓ Saved OCR output to {file_path}")
        return file_path
        
    except Exception as e:
        print(f"[ERROR] Failed to save text file: {e}")
        return None


def process_document(doc_id: int, file_path: str):
    
    db = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"[ERROR] Document ID {doc_id} not found in database")
            db.close()
            return
        
        print(f"\n{'='*60}")
        print(f"PROCESSING DOCUMENT ID: {doc_id}")
        print(f"File: {file_path}")
        print(f"{'='*60}")
        
    
        extracted_data = extract_structured_data(file_path)
        
        if "error" in extracted_data:
            doc.status = "failed_ocr"
            doc.extracted_json = extracted_data
            db.commit()
            print(f"[ERROR] OCR failed for document {doc_id}")
        else:
           
            full_text = extracted_data.get("ocr_text", str(extracted_data))
            save_text_file(full_text, "./rag_docs", doc_id)
            
            print(f"[INFO] ✓ Document {doc_id} processed successfully")
            print(f"[INFO] Policy Number: {extracted_data.get('policy_no', 'N/A')}")
            print(f"[INFO] Policy Type: {extracted_data.get('policy_type', 'N/A')}")
            
            
            doc.extracted_json = extracted_data
            db.commit()
            db.refresh(doc)
            
            
            print("[INFO] Running duplicate detection...")
            from duplicate_detection import is_duplicate_claim
            duplicate_result = is_duplicate_claim(doc_id, threshold=5)
            
            if duplicate_result.get("is_duplicate"):
                print(f"[WARNING] ⚠️  DUPLICATE DETECTED! Found {duplicate_result['duplicate_count']} similar document(s)")
                for dup in duplicate_result.get("similar_docs", []):
                    print(f"  → Similar to Doc #{dup['doc_id']} ({dup['filename']}) - Similarity: {dup['similarity_score']}")
            else:
                print(f"[INFO] ✓ No duplicates found")
            
        
            db.refresh(doc)
            current_extracted = doc.extracted_json if doc.extracted_json else {}
            current_extracted["duplicate_check"] = duplicate_result
            doc.extracted_json = current_extracted
            doc.status = "processed"  
            
            
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(doc, "extracted_json")
            
            db.commit()
            
            print(f"[DEBUG] ✓ Duplicate check saved: {duplicate_result}")
        
    except Exception as e:
        doc.status = "failed"
        doc.extracted_json = {"error": str(e)}
        db.commit()
        print(f"[ERROR] Exception during document processing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()
        print(f"{'='*60}\n")


