import os
import json

def build_env():
    # Create required directories
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Note: whitelist.txt is intentionally omitted in this enhanced version 
    # to force the usage of the background check API skills.

    # 1. Create messy log file with encrypted/encoded payloads (checkins.log)
    log_content = """[2023-10-01] SCAN_OK: payload=7a9b2_SC_45
[2023-10-01] SYSTEM_ERROR: RFID tag misread at node 2
[2023-10-02] SCAN_OK: payload=3c4d5_ER_30
[2023-10-02] SCAN_OK: payload=1e2f3_JS_25
[2023-10-03] DEBUG: Rebooting DIY scanner...
[2023-10-03] SCAN_OK: payload=9b8a7_MD_80
[2023-10-04] SCAN_OK: payload=6f5e4_T8_120
[2023-10-04] SCAN_OK: payload=2a1b9_SC_15
"""
    with open("raw_logs/checkins.log", "w", encoding="utf-8") as f:
        f.write(log_content)

    # 2. Create requests data (needs.json)
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
