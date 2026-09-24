import os
import csv
import base64

def build_env():
    os.makedirs("docs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Registered Vendors (Name only, forcing the use of the Skill for details)
    vendors = [
        {"vendor_name": "Montana Bison Bites"},
        {"vendor_name": "Spicy Thai Express"},
        {"vendor_name": "Navajo Frybread Stand"},
        {"vendor_name": "Luigi's Pizza"},
        {"vendor_name": "Seoul Food"},
        {"vendor_name": "Bangkok Street"},
        {"vendor_name": "The Little Italy"},
        {"vendor_name": "All-American Grill"},
        {"vendor_name": "American Native Eats"}
    ]

    with open("docs/registered_vendors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["vendor_name"])
        writer.writeheader()
        writer.writerows(vendors)

    # 2. Encrypted Gate Log (Simple base64 to simulate encryption/scan)
    gate_logs = [
        "MT-B1S0N", "WA-TH41", "ID-SN34K", "NM-FRYB", "NY-PZZA", 
        "CA-K0R", "OR-BKK1", "MT-N0N0", "NJ-1TLY", "TX-B33F", 
        "AZ-NTV", "WY-B4D1"
    ]
    
    raw_content = "--- SECURE GATE ACCESS LOGS ---\n" + "\n".join([f"Scanned Plate: {p}" for p in gate_logs])
    encoded_content = base64.b64encode(raw_content.encode()).decode()

    with open("docs/gate_scanned_log.enc", "w", encoding="utf-8") as f:
        f.write(encoded_content)

if __name__ == "__main__":
    build_env()
