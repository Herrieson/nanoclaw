import sys
import json

def get_ocr_data(file_path):
    if "south_wing_invoice.pdf" in file_path:
        data = [
            {"date": "2023-10-02", "item_id": "CHEM_001", "supplier": "CleanCorp", "quantity": 2, "unit_price_charged": 16.00},
            {"date": "2023-10-12", "item_id": "SOAP_005", "supplier": "CleanCorp", "quantity": 1, "unit_price_charged": 25.00},
            {"date": "2023-10-15", "item_id": "BRUSH_004", "supplier": "CleanCorp", "quantity": 3, "unit_price_charged": 8.25}
        ]
        return json.dumps(data)
    return "Error: File format not recognized or file missing."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_ocr_data(sys.argv[1]))
    else:
        print("Usage: python ocr_invoice_scanner_skill.py <file_path>")
