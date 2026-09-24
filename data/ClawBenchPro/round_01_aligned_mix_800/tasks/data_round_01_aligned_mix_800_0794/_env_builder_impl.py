import os
import json
import csv

def build_env():
    # Create the messy records directory
    os.makedirs("event_records", exist_ok=True)

    # 1. VIP List (Clean text)
    with open("event_records/vip_invites.txt", "w", encoding="utf-8") as f:
        f.write("Mr. Anderson\nIsabella Torres\nJulian Vance\nSophia Sterling\nMarcus Reed\n")

    # 2. Receipts (Nested JSON)
    expenses = {
        "event_date": "2023-10-15",
        "expenses": [
            {
                "category": "Art Acquisition",
                "items": [
                    {"name": "Abstract Canvas - Midnight", "cost": 1200}
                ]
            },
            {
                "category": "Hospitality",
                "items": [
                    {"name": "Catering (Tapas)", "cost": 850},
                    {"name": "Wine Pairing", "cost": 450}
                ]
            }
        ]
    }
    with open("event_records/receipts.json", "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2)

    # 3. Tips and Donations (Messy CSV with whitespaces and dollar signs)
    with open("event_records/tips_and_donations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Guest Name", "Tip Amount"])
        writer.writerow(["Mr. Anderson", " $800 "])
        writer.writerow([" Isabella Torres ", " $450.00 "])
        writer.writerow(["Julian Vance", "1200"])
        writer.writerow(["Sophia Sterling", "$600"])
        writer.writerow(["Marcus Reed", " 0 "])
        writer.writerow(["Crash Override", "$100"])
        writer.writerow(["Lucia Gomez", "750"])

if __name__ == "__main__":
    build_env()
