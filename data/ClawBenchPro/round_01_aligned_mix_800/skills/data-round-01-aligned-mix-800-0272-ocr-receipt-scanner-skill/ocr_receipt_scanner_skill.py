import os
import sys

def execute(file_path):
    if not file_path.endswith('.pdf'):
        return "Error: Unsupported file format. Only .pdf scans are supported."
    
    # Mocking the OCR result for receipt_scan.pdf
    if "receipt_scan.pdf" in file_path:
        return """
        --- OCR SCAN START ---
        HARDWARE WORLD - STORE #441
        Items:
        1. Steering Wheel Assembly: $35.50
        2. Zinc-plated Bolts (Pack): $4.20
        3. Heavy Duty Glue: $5.00 (VOID - RETURNED)
        TOTAL PAID: $39.70
        --- OCR SCAN END ---
        """
    else:
        return "Error: File not found or unreadable."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(execute(sys.argv[1]))
