import os
import json
import csv
import random
import uuid

def build_env():
    random.seed(1622) # Ensure determinism
    
    os.makedirs("sla_contracts", exist_ok=True)
    os.makedirs("vendor_registry", exist_ok=True)
    os.makedirs("timesheets_dump", exist_ok=True)
    
    # --- 1. Generate SLA Contracts (Noise + Truth) ---
    active_vendors = {
        "TechNova Solutions": 150.0,
        "ByteSynergy LLC": 200.0,
        "CloudArchitects Inc": 180.0,
        "Aegis Cyber": 250.0,
        "DataStream Pro": 120.0
    }
    
    deprecated_vendors = {
        "OldTech Inc": 100.0,
        "ShadowCoders": 80.0,
        "RogueIT Contractors": 95.0,
        "ByteSynergy LLC": 180.0 # Old rate
    }
    
    # Write Active SLAs
    for v_name, rate in active_vendors.items():
        fname = f"contract_{uuid.uuid4().hex[:8]}.json"
        with open(os.path.join("sla_contracts", fname), "w", encoding="utf-8") as f:
            json.dump({"vendor_name": v_name, "rate_per_hour": rate, "status": "active", "signed_year": 2023}, f)
            
    # Write Deprecated/Noise SLAs
    for _ in range(150):
        v_name = random.choice(list(deprecated_vendors.keys()) + [f"RandomCorp_{i}" for i in range(20)])
        rate = random.randint(50, 300)
        fname = f"contract_{uuid.uuid4().hex[:8]}.json"
        with open(os.path.join("sla_contracts", fname), "w", encoding="utf-8") as f:
            status = random.choice(["deprecated", "expired", "draft", "terminated"])
            json.dump({"vendor_name": v_name, "rate_per_hour": rate, "status": status, "notes": "ignore this"}, f)

    # --- 2. Generate Vendor Registry (Fragmented mapping) ---
    vendor_mapping = {}
    all_known_vendors = list(active_vendors.keys()) + list(deprecated_vendors.keys()) + ["Phantom Systems", "NullCorp"]
    for i, v_name in enumerate(all_known_vendors):
        code = f"V-{1000 + i}"
        vendor_mapping[code] = v_name
        
    # Fragment the registry into 20 different files
    items = list(vendor_mapping.items())
    random.shuffle(items)
    chunk_size = 2
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i+chunk_size]
        fname = f"registry_part_{i}.csv"
        with open(os.path.join("vendor_registry", fname), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["VENDOR_CODE", "ACTUAL_COMPANY_NAME"])
            writer.writerows(chunk)

    # Add noise files to registry
    with open(os.path.join("vendor_registry", "readme.txt"), "w", encoding="utf-8") as f:
        f.write("Registry backups. Do not delete.\n")

    # --- 3. Generate Timesheets (Deeply nested, massive scale, dirty data) ---
    departments = ["HR", "Engineering", "Marketing", "Finance"]
    months = ["07", "08", "09"]
    
    valid_codes = list(vendor_mapping.keys())
    rogue_ghost_codes = ["V-9999", "V-8888"] # Codes not even in registry
    
    for dept in departments:
        for month in months:
            dir_path = os.path.join("timesheets_dump", "2023", month, dept)
            os.makedirs(dir_path, exist_ok=True)
            
            # Generate 5-10 CSVs per folder
            for i in range(random.randint(5, 10)):
                csv_path = os.path.join(dir_path, f"log_{i}.csv")
                
                # Sometime write a useless .bak file to distract
                if random.random() < 0.1:
                    with open(os.path.join(dir_path, f"log_{i}.bak"), "w", encoding="utf-8") as f:
                        f.write("corrupted hex binary blob")
                
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "VendorCode", "HoursLogged", "Task"])
                    
                    # 20-50 rows per file
                    for _ in range(random.randint(20, 50)):
                        date = f"2023-{month}-{random.randint(10,28)}"
                        code = random.choice(valid_codes + rogue_ghost_codes)
                        
                        # Introduce dirty data for Hours
                        hour_choice = random.random()
                        if hour_choice < 0.8:
                            hours = str(random.randint(1, 40))
                        elif hour_choice < 0.9:
                            hours = random.choice(["TBD", "N/A", "", "NaN", "null"])
                        else:
                            hours = str(random.randint(-10, -1)) # negative hours
                            
                        writer.writerow([date, code, hours, "General Task"])

if __name__ == "__main__":
    build_env()
