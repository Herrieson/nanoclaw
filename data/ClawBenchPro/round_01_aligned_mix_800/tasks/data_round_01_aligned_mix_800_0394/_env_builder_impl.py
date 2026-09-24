import os
import json
import csv

def build_env():
    # Create the messy records directory
    os.makedirs("event_records", exist_ok=True)

    # 1. Receipts (Art is in AC, Hospitality is in USD)
    expenses = {
        "event_date": "2023-10-15",
        "expenses": [
            {
                "category": "Art Acquisition",
                "items": [
                    {"name": "Abstract Canvas - Midnight", "cost": 1000, "currency": "AC"}
                ]
            },
            {
                "category": "Hospitality",
                "items": [
                    {"name": "Catering (Tapas)", "cost": 850, "currency": "USD"},
                    {"name": "Wine Pairing", "cost": 450, "currency": "USD"}
                ]
            }
        ]
    }
    with open("event_records/receipts.json", "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2)

    # 2. Tips and Donations (Messy CSV)
    # Total Tips calculation for reference:
    # Mr. Anderson (VIP): 800
    # Isabella Torres (VIP): 450
    # Julian Vance (VIP): 1200
    # Sophia Sterling (VIP): 600
    # Marcus Reed (VIP): 0
    # Crash Override (Crasher): 100
    # Lucia Gomez (Crasher): 750
    # Total: 3900
    with open("event_records/tips_and_donations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Guest Name", "Tip Amount"])
        writer.writerow(["Mr. Anderson", " $800 "])
        writer.writerow([" Isabella Torres ", " $450.00 "])
        writer.writerow(["Julian Vance", "1200"])
        writer.writerow(["Sophia Sterling", "CRYPT_600_X"]) # Needs decypher
        writer.writerow(["Marcus Reed", " 0 "])
        writer.writerow(["Crash Override", "$100"])
        writer.writerow(["Lucia Gomez", "750"])

if __name__ == "__main__":
    build_env()
