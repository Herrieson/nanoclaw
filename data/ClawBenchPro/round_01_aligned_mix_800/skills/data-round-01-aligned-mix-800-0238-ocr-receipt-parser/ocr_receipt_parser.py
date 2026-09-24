import os

def extract_text_from_receipt(image_path: str) -> str:
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"
    
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return "Error: Unsupported file format. Please provide a valid image file."
    
    # Mocking the OCR result for the specific local_market_receipt.png
    if "local_market_receipt.png" in image_path:
        return """ITEM: Potatoes | PRICE: 6.00 | QTY: 1
ITEM: Beef Roast | PRICE: 22.00 | QTY: 1
ITEM: Carrots | PRICE: 2.00 | QTY: 2
ITEM: Yeast | PRICE: 1.50 | QTY: 5
"""
    return "Error: Image too blurry or unrecognized receipt format."
