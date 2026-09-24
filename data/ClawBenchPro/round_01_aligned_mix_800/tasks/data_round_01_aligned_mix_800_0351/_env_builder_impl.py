import os
import json
import csv

def build_env():
    # Create the messy directory
    os.makedirs("site_records", exist_ok=True)

    # 1. Monday's Photo (A dummy file that the OCR skill will 'read')
    with open("site_records/monday_site_photo.png", "w") as f:
        f.write("MOCK_IMAGE_DATA_HANDWRITTEN_NOTES")

    # 2. Wednesday's JSON Audit
    wed_data = {
        "date": "2023-10-11",
        "location": "East Wall",
        "notes": "Walk-through completed.",
        "observations": [
            "Scaffolding unstable on the third level",
            "Extension cord sitting in a puddle near the generator"
        ]
    }
    with open("site_records/wednesday_audit.json", "w", encoding="utf-8") as f:
        json.dump(wed_data, f, indent=4)

    # 3. Expense IDs CSV (Reference for API)
    expense_data = [
        ["ID", "Date", "VendorID", "Amount"],
        ["TXN_001", "10/09", "V-99", "150.00"],  # Safety Harness
        ["TXN_002", "10/10", "V-22", "45.50"],   # Acrylic Paints
        ["TXN_003", "10/10", "V-99", "120.00"],  # Steel Toe Boots
        ["TXN_004", "10/11", "V-22", "30.00"],   # Canvas
        ["TXN_005", "10/11", "V-99", "15.50"],   # Caution Tape
        ["TXN_006", "10/12", "V-99", "25.00"],   # High-Vis Vest
        ["TXN_007", "10/12", "V-22", "18.00"]    # Modeling Clay
    ]
    with open("site_records/expense_ids.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(expense_data)

    # 4. Vendor Lookup PDF (Simplified for the PDF skill to read)
    # In a real env, we'd use a lib to make a PDF, here we mock the content for the PDF skill
    with open("site_records/vendor_lookup.pdf", "w", encoding="utf-8") as f:
        f.write("VENDOR CLASSIFICATION DOCUMENT\n")
        f.write("V-99: Industrial Safety Supplies Corp (Category S)\n")
        f.write("V-22: Creative Minds Art Emporium (Category A)\n")

if __name__ == "__main__":
    build_env()
