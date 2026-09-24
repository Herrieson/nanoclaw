import os

def extract_text(image_path: str) -> str:
    """
    Extracts text from a given image file using the community center OCR engine.
    """
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"
    
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return "Error: Unsupported file format. Please provide a PNG or JPG."
    
    # Mock behavior specific to the task's context
    if "whitelist_scan.png" in image_path:
        return "APPROVED VOLUNTEER LIST:\n- Alice Smith\n- Bob Jones\n- Charlie Brown\n"
    
    return "Error: OCR engine failed to recognize text in this image. Blurry or unreadable."
