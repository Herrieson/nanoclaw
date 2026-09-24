import os

def extract_text(file_path):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        # In this mock environment, the degraded PDF is actually stored as raw text.
        # This simulates a successful OCR extraction of the document.
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"OCR Engine Error: Failed to process document. {str(e)}"
