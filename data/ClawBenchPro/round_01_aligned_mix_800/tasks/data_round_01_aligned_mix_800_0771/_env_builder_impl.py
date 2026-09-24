import os
import json
import csv

def build_env():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("reference", exist_ok=True)

    zones = {
        "78701": "North-Transit",
        "78702": "East-Transit",
        "78703": "West-Transit",
        "78704": "South-Transit",
        "78705": "Central-Transit"
    }
    
    with open("reference/zones.json", "w") as f:
        json.dump(zones, f, indent=2)

    tickets = [
        {"ticket_id": "TX-100", "zip_code": "78701", "assigned_zone": "North-Transit", "issue": "Late delivery"},
        {"ticket_id": "TX-101", "zip_code": "78702", "assigned_zone": "South-Transit", "issue": "Driver went to wrong house"},
        {"ticket_id": "TX-102", "zip_code": "78703", "assigned_zone": "West-Transit", "issue": "Package damaged"},
        {"ticket_id": "TX-103", "zip_code": "78704", "assigned_zone": "North-Transit", "issue": "Never arrived"},
        {"ticket_id": "TX-104", "zip_code": "78705", "assigned_zone": "Central-Transit", "issue": "Left in rain"},
        {"ticket_id": "TX-105", "zip_code": "78701", "assigned_zone": "East-Transit", "issue": "Rude driver"},
        {"ticket_id": "TX-106", "zip_code": "78704", "assigned_zone": "South-Transit", "issue": "Lost item"},
        {"ticket_id": "TX-107", "zip_code": "78702", "assigned_zone": "East-Transit", "issue": "Tracking broken"},
        {"ticket_id": "TX-108", "zip_code": "78705", "assigned_zone": "West-Transit", "issue": "Delivered to neighbor"},
        {"ticket_id": "TX-109", "zip_code": "78703", "assigned_zone": "West-Transit", "issue": "Box crushed"}
    ]
    
    with open("raw_data/tickets.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "zip_code", "assigned_zone", "issue"])
        writer.writeheader()
        writer.writerows(tickets)

if __name__ == "__main__":
    build_env()
