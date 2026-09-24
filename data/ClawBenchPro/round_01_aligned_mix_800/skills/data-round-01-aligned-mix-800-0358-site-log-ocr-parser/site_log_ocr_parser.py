import json
import os

def service(image_path):
    """
    Simulates an OCR service for handwritten logs.
    """
    db_path = ".secret_vault/ocr_db.json"
    if not os.path.exists(db_path):
        return "Error: OCR engine offline (Database missing)."
    
    with open(db_path, "r") as f:
        db = json.load(f)
    
    return db.get(image_path, "Error: Image format not recognized or file not found.")
