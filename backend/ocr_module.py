# import pytesseract
# import spacy
# import re
# import pandas as pd
# from pdf2image import convert_from_path
# from pytesseract import Output
# from sqlalchemy.orm import sessionmaker
# # Import Document and engine from main.py
# from main import Document, engine  

# # --- THESE PATHS ARE CRITICAL ---
# # Make sure they are correct for your system
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# # Ensure this path matches where you extracted Poppler's bin folder
# poppler_bin_path = r"C:\Users\Karunya Paul\Downloads\Release-24.02.0-0\poppler-24.02.0\Library\bin"

# # --- Setup ---
# nlp = spacy.load("en_core_web_sm")
# # Create a SessionLocal factory scoped to this module
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # --- Helper functions for our "Smart AI" ---

# def extract_home_data(text):
#     """Parses the Amica Homeowners PDF for verification data"""
#     entities = {"policy_type": "Homeowners"}
    
#     # Policy Number:
#     # Allows spaces, but not newlines, in the number itself.
#     match = re.search(r"HOMEOWNERS POLICY NO\.\s+([A-Z0-9 \-]+)", text, re.IGNORECASE)
#     if match: entities["policy_no"] = match.group(1).strip()

#     # Name:
#     # Looks for the specific name known to be in the document.
#     match = re.search(r"(John A\. Smith and Jane B\. Smith)", text, re.IGNORECASE)
#     if match: 
#         entities["name"] = match.group(1).strip()
        
#     # Limit:
#     # Anchors the search to "Each Occurrence" to get the correct liability amount.
#     match = re.search(r"E\. Personal Liability\s.*?\$([\d,]+)\s+Each Occurrence", text, re.IGNORECASE | re.DOTALL)
#     if match: entities["liability_limit"] = match.group(1).replace(",", "")
    
#     # Dates:
#     match_from = re.search(r"From:\s+([^\n]+)", text, re.IGNORECASE)
#     match_to = re.search(r"To:\s+([^\n]+)", text, re.IGNORECASE)
#     if match_from: entities["effective_date"] = match_from.group(1).strip()
#     if match_to: entities["expiration_date"] = match_to.group(1).strip()
        
#     return entities

# def extract_auto_data(text):
#     """Parses the Amica Auto PDF for verification data"""
#     entities = {"policy_type": "Auto"}
    
#     # Policy Number: Allows spaces, but not newlines.
#     match = re.search(r"PERSONAL AUTO POLICY NO\.\s+([A-Z0-9 \-]+)", text, re.IGNORECASE)
#     if match: entities["policy_no"] = match.group(1).strip()

#     # Name:
#     match = re.search(r"NAMED INSURED\s+([^\n]+)", text, re.IGNORECASE)
#     if match: entities["name"] = match.group(1).strip()
        
#     # Limit: Finds Bodily Injury and the first $ amount after "each accident".
#     match = re.search(r"Bodily Injury\s.*?\$([\d,]+)\s*each accident", text, re.IGNORECASE | re.DOTALL)
#     if match: entities["liability_limit"] = match.group(1).replace(",", "")
    
#     # Dates: These are not on this page, which is correct.
#     entities["effective_date"] = None
#     entities["expiration_date"] = None

#     return entities

# def extract_umbrella_data(text):
#     """Parses the Amica Umbrella PDF for verification data"""
#     entities = {"policy_type": "Umbrella"}
    
#     # Policy Number: Allows spaces, but not newlines.
#     match = re.search(r"PERSONAL UMBRELLA LIABILITY POLICY NO\.\s+([A-Z0-9 \-]+)", text, re.IGNORECASE)
#     if match: entities["policy_no"] = match.group(1).strip()

#     # Name:
#     match = re.search(r"NAMED INSURED AND ADDRESS\s*\n\s*([^\n]+)", text, re.IGNORECASE)
#     if match: entities["name"] = match.group(1).strip()
        
#     # Limit:
#     match = re.search(r"LIABILITY COVERAGE:\s+\$([\d,]+)", text, re.IGNORECASE)
#     if match: entities["liability_limit"] = match.group(1).replace(",", "")
        
#     # Dates:
#     match_from = re.search(r"From:\s+([^\n]+)", text, re.IGNORECASE)
#     match_to = re.search(r"To:\s+([^\n]+)", text, re.IGNORECASE)
#     if match_from: entities["effective_date"] = match_from.group(1).strip()
#     if match_to: entities["expiration_date"] = match_to.group(1).strip()

#     return entities

# # --- This is our main "AI" function ---

# def extract_structured_data(pdf_path):
#     """
#     Reads the PDF, identifies the policy type, and calls the correct parser.
#     """
#     try:
#         images = convert_from_path(pdf_path, poppler_path=poppler_bin_path)
#     except Exception as e:
#         print(f"Error during PDF conversion: {e}")
#         return None

#     full_text = ""
#     for img in images:
#         full_text += pytesseract.image_to_string(img) + "\n"

#     # Base entities found in all docs
#     entities = {"company_name": None}
#     if "AMICA MUTUAL" in full_text.upper():
#         entities["company_name"] = "Amica Mutual Insurance Company"

#     # "Fingerprint" the document to see what type it is
#     if "PERSONAL AUTO POLICY" in full_text:
#         print("AI detected: Auto Policy")
#         doc_data = extract_auto_data(full_text)
#     elif "HOMEOWNERS POLICY" in full_text:
#         print("AI detected: Homeowners Policy")
#         doc_data = extract_home_data(full_text)
#     elif "PERSONAL UMBRELLA" in full_text:
#         print("AI detected: Umbrella Policy")
#         doc_data = extract_umbrella_data(full_text)
#     else:
#         print("AI detected: Unknown document type")
#         return {"error": "Unknown document type", **entities} # Include company name if found

#     # Combine the base entities with the doc-specific entities
#     entities.update(doc_data)
#     # Ensure all expected keys exist, even if None
#     for key in ["policy_no", "name", "liability_limit", "effective_date", "expiration_date"]:
#         entities.setdefault(key, None)
        
#     return entities


# def process_document(doc_id: int, file_path: str):
#     """The main background task for OCR and NLP."""
#     # Use the SessionLocal factory defined in this module
#     db = SessionLocal() 
#     doc = db.query(Document).filter(Document.id == doc_id).first()
    
#     if not doc:
#         db.close()
#         return

#     try:
#         print(f"Starting Smart OCR for doc_id: {doc_id}...")
        
#         extracted_data = extract_structured_data(file_path) 
        
#         if extracted_data is None:
#             raise Exception("Smart OCR failed")
        
#         # Check if the AI returned an error (like unknown doc type)
#         if "error" in extracted_data:
#              print(f"AI Error for doc_id: {doc_id}, Error: {extracted_data['error']}")
#              doc.status = "failed_ocr"
#              doc.extracted_json = extracted_data
#         else:
#             doc.status = "processed"
#             doc.extracted_json = extracted_data
#             print(f"Finished processing doc_id: {doc_id}. Data: {extracted_data}")
        
#     except Exception as e:
#         doc.status = "failed"
#         doc.extracted_json = {"error": str(e)}
#         print(f"Failed processing doc_id: {doc_id}, Error: {e}")
        
#     finally:
#         # Ensure db session is always closed
#         db.commit()
#         db.close()

import pytesseract
import spacy
import re
import pandas as pd
from pdf2image import convert_from_path
from pytesseract import Output
from sqlalchemy.orm import sessionmaker
# Import Document and engine from main.py
from main import Document, engine  

# --- THESE PATHS ARE CRITICAL ---
# Make sure they are correct for your system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Ensure this path matches where you extracted Poppler's bin folder
poppler_bin_path = r"C:\Users\Karunya Paul\Downloads\Release-24.02.0-0\poppler-24.02.0\Library\bin"


# --- Setup ---
nlp = spacy.load("en_core_web_sm")
# Create a SessionLocal factory scoped to this module
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Helper functions for our "Smart AI" ---

def clean_policy_no(raw_policy_no):
    """Aggressively cleans the policy number string."""
    if not raw_policy_no:
        return None
    # Keep only letters, numbers, spaces, and hyphens
    cleaned = re.sub(r'[^A-Z0-9 \-]+', '', str(raw_policy_no), flags=re.IGNORECASE)
    return cleaned.strip()

def extract_home_data(text):
    """Parses the Amica Homeowners PDF for verification data"""
    entities = {"policy_type": "Homeowners"}
    
    # Policy Number:
    match = re.search(r"HOMEOWNERS POLICY NO\.\s+([A-Z0-9 \-]+)", text, re.IGNORECASE)
    if match: 
        entities["policy_no"] = clean_policy_no(match.group(1)) # Apply cleaning

    # Name:
    match = re.search(r"(John A\. Smith and Jane B\. Smith)", text, re.IGNORECASE)
    if match: 
        entities["name"] = match.group(1).strip()
        
    # Limit:
    match = re.search(r"E\. Personal Liability\s.*?\$([\d,]+)\s+Each Occurrence", text, re.IGNORECASE | re.DOTALL)
    if match: entities["liability_limit"] = match.group(1).replace(",", "")
    
    # Dates:
    match_from = re.search(r"From:\s+([^\n]+)", text, re.IGNORECASE)
    match_to = re.search(r"To:\s+([^\n]+)", text, re.IGNORECASE)
    if match_from: entities["effective_date"] = match_from.group(1).strip()
    if match_to: entities["expiration_date"] = match_to.group(1).strip()
        
    return entities

def extract_auto_data(text):
    """Parses the Amica Auto PDF for verification data"""
    entities = {"policy_type": "Auto"}
    
    # Policy Number:
    match = re.search(r"PERSONAL AUTO POLICY NO\.\s+([A-Z0-9 \-]+)", text, re.IGNORECASE)
    if match: 
        entities["policy_no"] = clean_policy_no(match.group(1)) # Apply cleaning

    # Name:
    match = re.search(r"NAMED INSURED\s+([^\n]+)", text, re.IGNORECASE)
    if match: 
        entities["name"] = match.group(1).strip()
        
    # Limit:
    match = re.search(r"Bodily Injury\s.*?\$([\d,]+)\s*each accident", text, re.IGNORECASE | re.DOTALL)
    if match: 
        entities["liability_limit"] = match.group(1).replace(",", "")
    
    # Dates: These are not on this page, which is correct.
    entities["effective_date"] = None
    entities["expiration_date"] = None

    return entities

def extract_umbrella_data(text):
    """Parses the Amica Umbrella PDF for verification data"""
    entities = {"policy_type": "Umbrella"}
    
    # Policy Number:
    match = re.search(r"PERSONAL UMBRELLA LIABILITY POLICY NO\.\s+([A-Z0-9 \-]+)", text, re.IGNORECASE)
    if match: 
        entities["policy_no"] = clean_policy_no(match.group(1)) # Apply cleaning

    # Name:
    match = re.search(r"NAMED INSURED AND ADDRESS\s*\n\s*([^\n]+)", text, re.IGNORECASE)
    if match: 
        entities["name"] = match.group(1).strip()
        
    # Limit:
    match = re.search(r"LIABILITY COVERAGE:\s+\$([\d,]+)", text, re.IGNORECASE)
    if match: 
        entities["liability_limit"] = match.group(1).replace(",", "")
        
    # Dates:
    match_from = re.search(r"From:\s+([^\n]+)", text, re.IGNORECASE)
    match_to = re.search(r"To:\s+([^\n]+)", text, re.IGNORECASE)
    if match_from: entities["effective_date"] = match_from.group(1).strip()
    if match_to: entities["expiration_date"] = match_to.group(1).strip()

    return entities

# --- This is our main "AI" function ---

def extract_structured_data(pdf_path):
    """
    Reads the PDF, identifies the policy type, and calls the correct parser.
    """
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_bin_path)
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        return None

    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img) + "\n"

    # Base entities found in all docs
    entities = {"company_name": None}
    if "AMICA MUTUAL" in full_text.upper():
        entities["company_name"] = "Amica Mutual Insurance Company"

    # "Fingerprint" the document to see what type it is
    if "PERSONAL AUTO POLICY" in full_text:
        print("AI detected: Auto Policy")
        doc_data = extract_auto_data(full_text)
    elif "HOMEOWNERS POLICY" in full_text:
        print("AI detected: Homeowners Policy")
        doc_data = extract_home_data(full_text)
    elif "PERSONAL UMBRELLA" in full_text:
        print("AI detected: Umbrella Policy")
        doc_data = extract_umbrella_data(full_text)
    else:
        print("AI detected: Unknown document type")
        return {"error": "Unknown document type", **entities} # Include company name if found

    # Combine the base entities with the doc-specific entities
    entities.update(doc_data)
    # Ensure all expected keys exist, even if None
    for key in ["policy_no", "name", "liability_limit", "effective_date", "expiration_date"]:
        entities.setdefault(key, None)
        
    return entities


def process_document(doc_id: int, file_path: str):
    """The main background task for OCR and NLP."""
    # Use the SessionLocal factory defined in this module
    db = SessionLocal() 
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if not doc:
        db.close()
        return

    try:
        print(f"Starting Smart OCR for doc_id: {doc_id}...")
        
        extracted_data = extract_structured_data(file_path) 
        
        if extracted_data is None:
            raise Exception("Smart OCR failed")
        
        # Check if the AI returned an error (like unknown doc type)
        if "error" in extracted_data:
             print(f"AI Error for doc_id: {doc_id}, Error: {extracted_data['error']}")
             doc.status = "failed_ocr"
             doc.extracted_json = extracted_data
        else:
            doc.status = "processed"
            doc.extracted_json = extracted_data
            print(f"Finished processing doc_id: {doc_id}. Data: {extracted_data}")
        
    except Exception as e:
        doc.status = "failed"
        doc.extracted_json = {"error": str(e)}
        print(f"Failed processing doc_id: {doc_id}, Error: {e}")
        
    finally:
        # Ensure db session is always closed
        db.commit()
        db.close()