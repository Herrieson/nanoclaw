import os
import csv
import json
import random

def build_env():
    # 🚨 Environment: Waste-land style archive
    base_dir = "legacy_archive"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("accounting", exist_ok=True)

    # Sub-directories for fragmentation
    sub_dirs = ["logs_2023_bak", "temp_fragments", "site_c_field_notes/raw", "unverified_exports/sector_7"]
    for sd in sub_dirs:
        os.makedirs(os.path.join(base_dir, sd), exist_ok=True)

    # 1. Real Data - Fragmented across formats
    # Fragment A: The CSV (nested deep)
    csv_path = os.path.join(base_dir, "site_c_field_notes/raw/export_final.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Provider", "Labor_Fee", "Mat_Cost", "W9_Status"])
        writer.writerow(["Apex Framing", "4500.50", "8200.00", "verified"]) # Valid
        writer.writerow(["Rogue Welding", "1200.00", "500.00", "pending"])   # Invalid (No W9)

    # Fragment B: The JSON (partial data)
    json_path = os.path.join(base_dir, "temp_fragments/partial_invoice_04.json")
    with open(json_path, "w") as f:
        json.dump([
            {"name": "Desert Fox Concrete", "costs": {"labor": 3100.0, "materials": 6200.0}, "legal": {"has_w9": True}}, # Valid
            {"name": "Sloppy Joe Painters", "costs": {"labor": 800.0, "materials": 200.0}, "legal": {"has_w9": False}}   # Invalid
        ], f)

    # Fragment C: The semi-structured TXT log (harder to parse)
    txt_path = os.path.join(base_dir, "unverified_exports/sector_7/ledger_notes.txt")
    with open(txt_path, "w") as f:
        f.write("LOG START - 2023-10-12\n")
        f.write("ENTRY: Baja Dirt Works | LABOR: 3000 | MATERIALS: 1500 | W9: YES\n") # Valid
        f.write("ENTRY: Maverick Excavation | LABOR: 4000 | MATERIALS: 1000 | W9: Y\n") # Valid
        f.write("LOG END\n")

    # 2. Scale Simulation - Creating 200+ Noise Files
    # These are decoys that look like data but are empty or contain "corrupt" flags
    noise_templates = [
        "backup_old_data_{}.log",
        "system_error_dump_{}.tmp",
        "contractor_list_draft_{}.csv",
        "temp_node_{}.json"
    ]
    
    for i in range(200):
        subdir = random.choice(sub_dirs + ["."])
        template = random.choice(noise_templates)
        file_path = os.path.join(base_dir, subdir, template.format(i))
        
        with open(file_path, "w") as f:
            if ".json" in file_path:
                json.dump({"status": "corrupt", "data": None, "id": random.randint(1000, 9999)}, f)
            elif ".csv" in file_path:
                f.write("id,junk1,junk2\n")
                f.write(f"{i},null,null\n")
            else:
                f.write(f"Random noise from system crash {random.random()}\n")

    # 3. Specific decoy with "W-9" but NO cost data
    decoy_path = os.path.join(base_dir, "logs_2023_bak/compliance_check.json")
    with open(decoy_path, "w") as f:
        json.dump({"contractor": "Ghost Services", "has_w9": True, "notes": "No work performed yet"}, f)

if __name__ == "__main__":
    build_env()
