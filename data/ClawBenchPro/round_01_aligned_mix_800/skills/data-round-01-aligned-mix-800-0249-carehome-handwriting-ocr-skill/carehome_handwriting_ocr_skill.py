import os

def perform_ocr(image_path: str) -> str:
    """
    Simulates OCR on a handwritten note image.
    """
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"
    
    if "midweek_notes.jpg" in image_path:
        return """[OCR Extracted Text]
2023-12-03: Used 3 units of Bleach but forgot the room number.
2023-12-04: Room 105 used 1 unit of Bleach.
"""
    return "Error: Image format not supported or image is blank."
