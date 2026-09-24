import sys
import os
import re

def perform_ocr(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simulating complex OCR parsing logic
        item_match = re.search(r"Item:\s*(.*?)\s*\|", content)
        cat_match = re.search(r"Cat:\s*(.*?)\s*\|", content)
        amt_match = re.search(r"Amt:\s*([\d\.]+)", content)
        
        if item_match and cat_match and amt_match:
            return f"OCR Result: {{'item': '{item_match.group(1)}', 'category': '{cat_match.group(1)}', 'amount': {amt_match.group(1)}}}"
        else:
            return "Error: OCR failed to identify fields in the document structure."
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python heritage_receipt_ocr_skill.py <file_path>")
    else:
        print(perform_ocr(sys.argv[1]))
