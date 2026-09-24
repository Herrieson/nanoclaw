import os
import json

def build_env():
    # Create required directories
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create whitelist
    whitelist_content = """Sarah Connor
Miles Dyson
Ellen Ripley
Kyle Reese
"""
    with open("whitelist.txt", "w", encoding="utf-8") as f:
        f.write(whitelist_content)

    # 2. Create messy log file (checkins.log)
    log_content = """[2023-10-01] SCAN_OK: Sarah Connor logged 4.5 hours
[2023-10-01] SYSTEM_ERROR: RFID tag misread at node 2
[2023-10-02] SCAN_OK: Ellen Ripley logged 3.0 hours
[2023-10-02] SCAN_OK: John Smith logged 2.5 hours
[2023-10-03] DEBUG: Rebooting DIY scanner...
[2023-10-03] SCAN_OK: Miles Dyson logged 8.0 hours
[2023-10-04] SCAN_OK: T-800 logged 12.0 hours
[2023-10-04] SCAN_OK: Sarah Connor logged 1.5 hours
"""
    with open("raw_logs/checkins.log", "w", encoding="utf-8") as f:
        f.write(log_content)

    # 3. Create requests data (needs.json)
    requests_data = [
        {"family_id": "A12", "request": "Baby formula and diapers", "urgent": True, "notes": "Out of stock at home"},
        {"family_id": "B04", "request": "Adult Winter coat, size L", "urgent": False, "notes": "For next season"},
        {"family_id": "C99", "request": "Canned vegetables and rice", "urgent": False, "notes": "Standard pantry box"},
        {"family_id": "D45", "request": "Pediatric asthma inhaler assistance", "urgent": True, "notes": "Medical necessity"},
        {"family_id": "E11", "request": "Bus passes for job interviews", "urgent": True, "notes": "Needs by tomorrow"}
    ]
    with open("raw_logs/needs.json", "w", encoding="utf-8") as f:
        json.dump(requests_data, f, indent=2)

if __name__ == "__main__":
    build_env()
