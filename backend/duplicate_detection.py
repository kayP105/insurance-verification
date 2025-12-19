import imagehash
from PIL import Image
from pdf2image import convert_from_path
from db import SessionLocal
from models import Document
import os

poppler_bin_path = r"C:\Users\Karunya Paul\Downloads\Release-24.02.0-0\poppler-24.02.0\Library\bin"

def is_duplicate_claim(doc_id: int, threshold: int = 5):
   
    db = SessionLocal()
    
    try:
        current_doc = db.query(Document).filter(Document.id == doc_id).first()
        
        if not current_doc or not current_doc.local_path:
            return {
                "is_duplicate": False,
                "error": "Document not found or no file path"
            }
        
       
        try:
            if current_doc.local_path.lower().endswith('.pdf'):
                print(f"[DEBUG] Converting PDF to image for hashing: {current_doc.local_path}")
                images = convert_from_path(
                    current_doc.local_path, 
                    first_page=1, 
                    last_page=1, 
                    poppler_path=poppler_bin_path
                )
                current_image = images[0].convert("RGB")
            else:
                current_image = Image.open(current_doc.local_path).convert("RGB")
            
            current_hash = imagehash.phash(current_image)
            print(f"[DEBUG] Current document hash: {current_hash}")
            
        except Exception as e:
            print(f"[ERROR] Failed to hash current document: {e}")
            return {
                "is_duplicate": False,
                "error": f"Failed to process image: {e}"
            }
        
        
        all_docs = db.query(Document).filter(
            Document.id != doc_id,
            Document.local_path != None,
            Document.local_path != ""
        ).all()
        
        print(f"[DEBUG] Comparing against {len(all_docs)} other document(s) in database")
        
        duplicates = []
        
        for other_doc in all_docs:
            if not other_doc.local_path or not os.path.exists(other_doc.local_path):
                print(f"[DEBUG] Skipping doc {other_doc.id} - file not found")
                continue
                
            try:
                if other_doc.local_path.lower().endswith('.pdf'):
                    images = convert_from_path(
                        other_doc.local_path, 
                        first_page=1, 
                        last_page=1, 
                        poppler_path=poppler_bin_path
                    )
                    other_image = images[0].convert("RGB")
                else:
                    other_image = Image.open(other_doc.local_path).convert("RGB")
                
                other_hash = imagehash.phash(other_image)
                hash_diff = current_hash - other_hash
                
                print(f"[DEBUG] Doc {other_doc.id} ({other_doc.filename}): hash={other_hash}, diff={hash_diff}")
                
                if hash_diff <= threshold:
                    duplicates.append({
                        "doc_id": other_doc.id,
                        "filename": other_doc.filename,
                        "similarity_score": float(hash_diff),
                        "policy_no": other_doc.extracted_json.get("policy_no") if other_doc.extracted_json else None
                    })
                    print(f"[DEBUG] ⚠️  DUPLICATE MATCH: Doc {other_doc.id} with similarity {hash_diff}")
                    
            except Exception as e:
                print(f"[WARNING] Failed to compare with doc {other_doc.id}: {e}")
                continue
        
        if duplicates:
            duplicates.sort(key=lambda x: x['similarity_score'])
            
            return {
                "is_duplicate": True,
                "duplicate_count": len(duplicates),
                "similar_docs": duplicates,
                "message": f"Found {len(duplicates)} potential duplicate(s)"
            }
        else:
            return {
                "is_duplicate": False,
                "duplicate_count": 0,
                "message": "No duplicates found"
            }
            
    finally:
        db.close()
