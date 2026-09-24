import os
import json

def build_env():
    # Create directories
    os.makedirs("raw_data", exist_ok=True)
    
    # 1. Create a dummy PDF (placeholder for the OCR skill to target)
    with open("raw_data/timesheet_scan_legacy.pdf", "w") as f:
        f.write("%PDF-1.4 [Internal Legacy Scan - Use audit_ledger_ocr_skill to read]")

    # 2. Timesheet B (JSON) - mixed data
    # Authorized: CloudArchitects Inc (20h), TechNova Solutions (10h)
    # Unauthorized: ShadowCoders (50h)
    json_data = [
        {"vendor_id": "CloudArchitects Inc", "h": 20, "desc": "DB migration"},
        {"vendor_id": "ShadowCoders", "h": 50, "desc": "Frontend hotfix"},
        {"vendor_id": "TechNova Solutions", "h": 10, "desc": "Code review"}
    ]
    with open("raw_data/timesheet_api_dump.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    # Note: The 'approved_rates.json' is intentionally omitted as it is now served via Skill API.
    # Note: The OCR skill will "read" the PDF and return:
    # TechNova Solutions: 40h
    # RogueIT Contractors: 25h
    # ByteSynergy LLC: 15h

if __name__ == "__main__":
    build_env()
