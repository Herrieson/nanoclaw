import os

def handwriting_ocr_skill(image_path: str) -> str:
    """
    Simulates an OCR engine extracting text from a scanned document.
    """
    if not os.path.exists(image_path):
        return f"Error: Image not found at path {image_path}. Please check the path and try again."
    
    if "site_c_handwritten.png" in image_path:
        # Returns the mocked content that used to be in the plaintext file
        return "david rodriguez : 2 hours\nChloe Dubois : 3.5 hrs\ngary smith: 1 hour\n"
    
    return "Error: Unsupported or unreadable image for OCR processing."
