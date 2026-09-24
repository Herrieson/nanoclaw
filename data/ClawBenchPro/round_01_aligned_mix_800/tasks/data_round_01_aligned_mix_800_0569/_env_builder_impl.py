import os
import json
import yaml
import random
import csv

def build_env():
    random.seed(1588)  # Ensure reproducibility for validation

    # 1. Create Directories
    os.makedirs("insurance_policies", exist_ok=True)
    os.makedirs("raw_exports", exist_ok=True)
    
    # 2. System Config (Multi-hop entry point)
    config_data = {
        "clinic_name": "Speech & Swallow Therapy Associates",
        "merge_status": "COMPLETED",
        "active_provider": "apex_health_v2_tier1",
        "last_update": "2023-10-31T23:59:59Z"
    }
    with open("system_config.yaml", "w") as f:
        yaml.dump(config_data, f)

    # 3. Insurance Policies (Decoys and True Whitelist)
    providers = {
        "legacy_medicare": ["92507", "92521"],
        "apex_health_v1_beta": ["92507", "92521", "92522", "99999"],
        "apex_health_v2_tier1": ["92507", "92521", "92522", "92523", "92524", "92610"], # THE TRUE WHITELIST
        "blue_cross_draft": ["92507", "92526", "92610"]
    }
    
    for provider, codes in providers.items():
        prov_dir = os.path.join("insurance_policies", provider)
        os.makedirs(prov_dir, exist_ok=True)
        # Create different formats to add noise
        if "v2" in provider:
            with open(os.path.join(prov_dir, "whitelist.json"), "w") as f:
                json.dump({"effective_date": "2023-10-01", "authorized_codes": codes}, f)
        else:
            with open(os.path.join(prov_dir, "codes.csv"), "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Code", "Description"])
                for c in codes:
                    writer.writerow([c, "Therapy"])

    # 4. Generate Raw Data (Scale and Fragmentation)
    patients = [
        ("Miller", "J"), ("Smith", "A"), ("Wilson", "K"), 
        ("Brown", "L"), ("Davis", "M"), ("Garcia", "C"), 
        ("Lee", "S"), ("Taylor", "R")
    ]
    valid_codes = providers["apex_health_v2_tier1"]
    invalid_codes = ["99999", "88888", "12345", "92599"]
    
    def mess_up_name(last, first):
        formats = [
            f"{last}, {first}.",
            f"  {last.lower()} ,  {first.lower()}.",
            f"{last.upper()}, {first}",
            f"{last},  {first} ."
        ]
        return random.choice(formats)

    def mess_up_duration(dur):
        formats = [
            f"{dur}", f"{dur}h", f"{dur} hrs", f"{dur}hr", f" {dur} "
        ]
        return random.choice(formats)

    def mess_up_code(code):
        formats = [f"{code}", f" {code} ", f"{code}"]
        return random.choice(formats)

    # Generate records
    base_records = []
    # Generate ~200 base valid/invalid records
    for _ in range(200):
        pt = random.choice(patients)
        date = f"2023-10-{random.randint(1, 31):02d}"
        dur = random.choice([0.5, 1.0, 1.5, 2.0, 2.5])
        is_valid = random.random() < 0.8
        code = random.choice(valid_codes) if is_valid else random.choice(invalid_codes)
        base_records.append({"date": date, "pt": pt, "code": code, "dur": dur})

    # Distribute into batches
    for batch_id in range(1, 31):
        batch_dir = os.path.join("raw_exports", f"batch_{batch_id:03d}")
        os.makedirs(batch_dir, exist_ok=True)
        
        # 5 to 15 files per batch
        for file_idx in range(random.randint(5, 15)):
            status = random.choices(["FINAL", "DRAFT", "ERROR"], weights=[0.4, 0.4, 0.2])[0]
            
            # Select 1 to 5 random records from base to put in this file
            file_records = []
            for _ in range(random.randint(1, 5)):
                rec = random.choice(base_records)
                file_records.append({
                    "Date": rec["date"],
                    "PatientName": mess_up_name(rec["pt"][0], rec["pt"][1]),
                    "ProcCode": mess_up_code(rec["code"]),
                    "DurationHours": mess_up_duration(rec["dur"])
                })
            
            # Some DRAFT/ERROR files have completely mangled schemas as noise
            if status != "FINAL" and random.random() < 0.3:
                payload = {"corrupted_dump": "missing_data"}
            else:
                payload = {
                    "metadata": {
                        "export_id": f"EXP_{batch_id}_{file_idx}",
                        "status": status,
                        "timestamp": f"2023-10-{batch_id:02d}T12:00:00Z"
                    },
                    "data": file_records
                }
                
            file_name = f"export_{batch_id:02d}_{file_idx:02d}_{status.lower()}.json"
            with open(os.path.join(batch_dir, file_name), "w") as f:
                json.dump(payload, f, indent=2)

    # Add a completely unrelated distractor file
    with open(os.path.join("raw_exports", "knitting_patterns.txt"), "w") as f:
        f.write("Remember to buy more merino wool for the scarf project. Purl 2, knit 1.")

if __name__ == "__main__":
    build_env()
