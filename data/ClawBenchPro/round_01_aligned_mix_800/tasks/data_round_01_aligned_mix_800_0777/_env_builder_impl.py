import os
import csv

def build_env():
    os.makedirs("docs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    vendors = [
        {"vendor_name": "Montana Bison Bites", "license_plate": "MT-B1S0N", "cuisine_type": "American"},
        {"vendor_name": "Spicy Thai Express", "license_plate": "WA-TH41", "cuisine_type": "Thai"},
        {"vendor_name": "Navajo Frybread Stand", "license_plate": "NM-FRYB", "cuisine_type": "Native American"},
        {"vendor_name": "Luigi's Pizza", "license_plate": "NY-PZZA", "cuisine_type": "Italian"},
        {"vendor_name": "Seoul Food", "license_plate": "CA-K0R", "cuisine_type": "Korean"},
        {"vendor_name": "Bangkok Street", "license_plate": "OR-BKK1", "cuisine_type": "Thai"},
        {"vendor_name": "The Little Italy", "license_plate": "NJ-1TLY", "cuisine_type": "Italian"},
        {"vendor_name": "All-American Grill", "license_plate": "TX-B33F", "cuisine_type": "American"},
        {"vendor_name": "American Native Eats", "license_plate": "AZ-NTV", "cuisine_type": "Native American"}
    ]

    with open("docs/registered_vendors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["vendor_name", "license_plate", "cuisine_type"])
        writer.writeheader()
        writer.writerows(vendors)

    gate_logs = [
        "MT-B1S0N",
        "WA-TH41",
        "ID-SN34K",  # unauthorized
        "NM-FRYB",
        "NY-PZZA",
        "CA-K0R",
        "OR-BKK1",
        "MT-N0N0",   # unauthorized
        "NJ-1TLY",
        "TX-B33F",
        "AZ-NTV",
        "WY-B4D1"    # unauthorized
    ]

    with open("docs/gate_access_logs.txt", "w", encoding="utf-8") as f:
        f.write("--- GATE ACCESS LOGS ---\n")
        f.write("Date: 2023-10-15\n")
        f.write("Officer on duty: Miller\n\n")
        for plate in gate_logs:
            f.write(f"Scanned Plate: {plate}\n")

if __name__ == "__main__":
    build_env()
