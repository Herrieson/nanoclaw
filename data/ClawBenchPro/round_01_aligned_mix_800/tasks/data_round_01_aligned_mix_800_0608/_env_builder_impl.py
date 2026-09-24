import os
import csv
import json

def build_env():
    # Create necessary directories directly in the current working directory
    os.makedirs("records", exist_ok=True)
    os.makedirs("supplies", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Generate Volunteer Data
    volunteers = [
        {"name": "Mike Smith", "bg_check": "Pass", "first_aid": "Yes"},
        {"name": "Jenny Lee", "bg_check": "Pending", "first_aid": "Yes"},
        {"name": "Tom Hanks", "bg_check": "Pass", "first_aid": "No"},
        {"name": "Linda Chen", "bg_check": "Pass", "first_aid": "Yes"},
        {"name": "Bob Dylan", "bg_check": "Fail", "first_aid": "No"},
        {"name": "Sarah Connor", "bg_check": "Pass", "first_aid": "Yes"},
        {"name": "David Webb", "bg_check": "Pass", "first_aid": "Pending"}
    ]
    with open("records/volunteers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "bg_check", "first_aid"])
        writer.writeheader()
        writer.writerows(volunteers)

    # Generate Supply Receipts Data
    supplies = [
        {"item": "Tents", "price": 120.50, "qty": 4},
        {"item": "Trail Mix", "price": 15.25, "qty": 10},
        {"item": "First Aid Kits", "price": 35.00, "qty": 3},
        {"item": "Bug Spray", "price": 8.75, "qty": 5},
        {"item": "Camp Lanterns", "price": 22.00, "qty": 2}
    ]
    with open("supplies/receipts.json", "w") as f:
        json.dump(supplies, f, indent=4)

    # Add some noise
    with open("records/note_from_principal.txt", "w") as f:
        f.write("Please ensure we stay under the $1000 budget for the trip. - Principal")

if __name__ == "__main__":
    build_env()
