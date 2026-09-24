import os
import json
import csv

def build_env():
    # Directories
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Mock PDF Scan (The obstacle)
    # Creating a dummy file that the Agent must "OCR" via skill
    with open("raw_records/attendee_scans.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 [Binary Data - Simulated Hand-written notes of vision screening event]")

    # 2. Consent Forms (JSON - remains for cross-referencing)
    consent_data = [
        {"name": "alice smith", "status": "signed", "date": "2023-10-01"},
        {"name": "Charlie brown", "status": "signed", "date": "2023-10-01"},
        {"name": "diana prince", "status": "pending", "date": "2023-10-01"},
        {"name": "evan wright", "status": "signed", "date": "2023-10-01"},
        {"name": "frank ocean", "status": "signed", "date": "2023-10-01"}
    ]
    with open("raw_records/consent_logs.json", "w", encoding="utf-8") as f:
        json.dump(consent_data, f, indent=4)

    # 3. Expense Receipts (CSV)
    # The prices here are BASE prices. Total sustainable calculation requires the skill.
    with open("raw_records/expense_receipts.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item_Code", "Description", "Base_Cost", "Category"])
        writer.writerow(["OPT-001", "Recycled Polycarbonate Lenses", "1200.00", "Sustainable"])
        writer.writerow(["OPT-002", "Standard Acetate Frames", "300.00", "Non-Sustainable"])
        writer.writerow(["OPT-003", "Bamboo Display Stands", "150.50", "Sustainable"])
        writer.writerow(["OPT-004", "Promotional Flyers (Recycled)", "45.25", "Sustainable"])
        writer.writerow(["MISC-99", "Staff Lunch", "80.00", "Standard"])

if __name__ == "__main__":
    build_env()
