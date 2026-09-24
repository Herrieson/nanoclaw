import os
import json
import csv
import random
import uuid

def build_env():
    random.seed(42) # Ensure reproducible wasteland

    # 1. Setup Directories
    os.makedirs("contracts", exist_ok=True)
    os.makedirs("collection_logs", exist_ok=True)

    # 2. Generate Brands & Contracts
    # approved: ACTIVE + ECO_PARTNER + not revoked
    # revoked: ACTIVE + ECO_PARTNER + in revoked_brands.txt
    # inactive: INACTIVE + ECO_PARTNER
    # non-eco: ACTIVE + REGULAR
    
    brand_definitions = [
        {"name": "WoodSpecs", "code": "ECO-01", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "LeafFrames", "code": "ECO-02", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "OceanPlastics", "code": "ECO-03", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "GreenGaze", "code": "ECO-04", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "BioLens", "code": "ECO-05", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "EcoOptics", "code": "ECO-06", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "NaturaSight", "code": "ECO-07", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "BambooVision", "code": "ECO-08", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": False},
        
        {"name": "FakeGreen", "code": "REV-01", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": True},
        {"name": "TrashToCash", "code": "REV-02", "status": "ACTIVE", "type": "ECO_PARTNER", "revoked": True},
        
        {"name": "OldEco", "code": "INA-01", "status": "INACTIVE", "type": "ECO_PARTNER", "revoked": False},
        {"name": "DeadBrand", "code": "INA-02", "status": "INACTIVE", "type": "ECO_PARTNER", "revoked": False},
        
        {"name": "FastFashion", "code": "REG-01", "status": "ACTIVE", "type": "REGULAR", "revoked": False},
        {"name": "CheapoPlastics", "code": "REG-02", "status": "ACTIVE", "type": "REGULAR", "revoked": False},
        {"name": "DesignerLux", "code": "REG-03", "status": "ACTIVE", "type": "REGULAR", "revoked": False},
    ]

    revoked_codes = []

    # Write contracts to fragmented files with random UUID names
    for bd in brand_definitions:
        if bd["revoked"]:
            revoked_codes.append(bd["code"])
        
        contract_data = {
            "contract_id": str(uuid.uuid4()),
            "brand_name": bd["name"],
            "brand_code": bd["code"],
            "status": bd["status"],
            "type": bd["type"],
            "contact": f"contact@{bd['name'].lower()}.com"
        }
        filename = f"contracts/contract_{str(uuid.uuid4())[:8]}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(contract_data, f, indent=2)

    # Write revoked list
    with open("revoked_brands.txt", "w", encoding="utf-8") as f:
        f.write("# DO NOT ACCEPT THESE BRANDS - GREENWASHING DETECTED\n")
        for code in revoked_codes:
            f.write(f"{code}\n")

    # 3. Generate Collection Logs (Scale & Fragmentation & Noise)
    bins = ["bin_north", "bin_south", "bin_east", "bin_west"]
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    # We will mix in some completely unknown codes
    unknown_codes = ["UNK-99", "UNK-88", "JUNK-01"]
    all_possible_codes = [b["code"] for b in brand_definitions] + unknown_codes

    patients = ["Mary", "Billy", "Doc", "John", "Jane", "Cletus", "Sue", "Bob", "Alice"]

    for b in bins:
        for d in days:
            dir_path = os.path.join("collection_logs", b, d)
            os.makedirs(dir_path, exist_ok=True)
            
            # Decide how many records for each file type
            records_csv = []
            records_json = []
            records_tsv = []

            for _ in range(random.randint(5, 15)):
                records_csv.append({
                    "patient": random.choice(patients),
                    "brand_code": random.choice(all_possible_codes),
                    "frames_count": random.randint(1, 5)
                })
            for _ in range(random.randint(5, 15)):
                records_json.append({
                    "patient": random.choice(patients),
                    "brand_code": random.choice(all_possible_codes),
                    "frames_count": random.randint(1, 5)
                })
            for _ in range(random.randint(5, 15)):
                records_tsv.append({
                    "patient": random.choice(patients),
                    "brand_code": random.choice(all_possible_codes),
                    "frames_count": random.randint(1, 5)
                })

            # Write CSV
            with open(os.path.join(dir_path, "data.csv"), "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["patient", "brand_code", "frames_count"])
                writer.writeheader()
                writer.writerows(records_csv)
            
            # Write JSON
            with open(os.path.join(dir_path, "data.json"), "w", encoding="utf-8") as f:
                json.dump({"log_entries": records_json}, f, indent=2)

            # Write TSV
            with open(os.path.join(dir_path, "data.tsv"), "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["patient", "brand_code", "frames_count"], delimiter='\t')
                writer.writeheader()
                writer.writerows(records_tsv)

            # Write Noise (.log file)
            with open(os.path.join(dir_path, "scanner_debug.log"), "w", encoding="utf-8") as f:
                f.write(f"[{d.upper()}] SCANNER BOOT SEQUENCE INITIATED...\n")
                f.write("ERROR: OPTICAL SENSOR MISALIGNMENT.\n")
                f.write("WARN: IGNORING DUST PARTICLE.\n")
                f.write(f"SYSTEM MEMORY DUMP: {str(uuid.uuid4())}\n")

if __name__ == "__main__":
    build_env()
