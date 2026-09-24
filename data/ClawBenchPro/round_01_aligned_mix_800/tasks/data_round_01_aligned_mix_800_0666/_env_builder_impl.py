import os
import json
import csv

def build_env():
    # Directories
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Messy Attendee Notes
    with open("raw_records/attendees_notes.txt", "w", encoding="utf-8") as f:
        f.write("--- VISION EVENT ATTENDEES ---\n")
        f.write("1. Alice Smith (needs new prescription)\n")
        f.write("2. bob jones - just browsing\n")
        f.write("3. Charlie Brown - brought his own eco-frames\n")
        f.write("4. DIANA PRINCE\n")
        f.write("5. Evan Wright - looking for sunglasses\n")

    # 2. Consent Forms (messy case matching, some missing, some pending)
    consent_data = [
        {"name": "alice smith", "status": "signed", "date": "2023-10-01"},
        {"name": "Charlie brown", "status": "signed", "date": "2023-10-01"},
        {"name": "diana prince", "status": "pending", "date": "2023-10-01"},
        {"name": "evan wright", "status": "signed", "date": "2023-10-01"},
        {"name": "frank ocean", "status": "signed", "date": "2023-10-01"}
    ]
    with open("raw_records/consent_logs.json", "w", encoding="utf-8") as f:
        json.dump(consent_data, f, indent=4)

    # 3. Expense Receipts
    with open("raw_records/expense_receipts.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Cost", "Category"])
        writer.writerow(["Recycled Polycarbonate Lenses", "1200.00", "Sustainable"])
        writer.writerow(["Standard Acetate Frames", "300.00", "Non-Sustainable"])
        writer.writerow(["Bamboo Display Stands", "150.50", "Sustainable"])
        writer.writerow(["Promotional Flyers (Recycled Paper)", "45.25", "Sustainable"])
        writer.writerow(["Staff Lunch", "80.00", "Standard"])

if __name__ == "__main__":
    build_env()
