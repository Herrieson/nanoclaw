import os
import json
import csv
import random

def build_env():
    # Set seed for reproducibility
    random.seed(1274)
    
    # 1. Define Directories
    manifests_dir = "manifests"
    logs_dir = "system_logs"
    os.makedirs(manifests_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    # Warehouses and dates
    warehouses = [
        "WH_01", "WH_02", "WH_03", "WH_04", 
        "WH_02_backup", "void_WH", "test_WH_99" # Decoy directories
    ]
    dates = ["2023-10-01", "2023-10-02", "2023-10-03"]
    
    # Data generation pools
    valid_zips = ["90210", "10001", "33101", "80202", "73301"]
    invalid_zips = ["1234", "ABCDE", "90210-1234", " 902 ", "0"]
    
    # Helper for weights
    def generate_weight(is_heavy=False):
        if is_heavy:
            # Over 50.0 lbs
            base_lbs = random.uniform(55.0, 100.0)
        else:
            # Under 48.0 lbs
            base_lbs = random.uniform(5.0, 48.0)
            
        unit_choice = random.choice(["num", "lbs", "kg", "oz"])
        if unit_choice == "num":
            return f"{base_lbs:.2f}"
        elif unit_choice == "lbs":
            return f"{base_lbs:.2f} lbs"
        elif unit_choice == "kg":
            kg_val = base_lbs / 2.20462
            return f"{kg_val:.2f} kg"
        elif unit_choice == "oz":
            oz_val = base_lbs / 0.0625
            return f"{oz_val:.2f} oz"
            
    def generate_zip(is_bad=False, add_spaces=False):
        if is_bad:
            z = random.choice(invalid_zips)
        else:
            z = random.choice(valid_zips)
        if add_spaces and not is_bad:
            # Add spaces that should be stripped to reveal a valid zip
            return f"  {z} "
        return z

    all_packages = []
    cancellations = set()
    pkg_counter = 10000
    
    # 2. Generate Files and Data
    for wh in warehouses:
        for date in dates:
            current_dir = os.path.join(manifests_dir, wh, date)
            os.makedirs(current_dir, exist_ok=True)
            
            # Generate 3 files per directory (CSV, JSON, TXT)
            # CSV file
            csv_data = []
            for _ in range(random.randint(20, 50)):
                pkg_counter += 1
                pid = f"PKG-{pkg_counter}"
                is_heavy = random.random() < 0.15
                is_bad_zip = random.random() < 0.15
                is_cancelled = random.random() < 0.10
                
                if is_cancelled:
                    cancellations.add(pid)
                    
                csv_data.append([
                    pid, 
                    generate_weight(is_heavy), 
                    generate_zip(is_bad_zip, add_spaces=random.choice([True, False])), 
                    f"Recipient_{pkg_counter}"
                ])
                
            with open(os.path.join(current_dir, "batch_A.csv"), "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Package_ID", "Weight", "ZipCode", "Recipient"])
                writer.writerows(csv_data)
                
            # JSON file
            json_data = []
            for _ in range(random.randint(20, 50)):
                pkg_counter += 1
                pid = f"PKG-{pkg_counter}"
                is_heavy = random.random() < 0.15
                is_bad_zip = random.random() < 0.15
                is_cancelled = random.random() < 0.10
                
                if is_cancelled:
                    cancellations.add(pid)
                
                json_data.append({
                    "Package_ID": pid,
                    "Weight": generate_weight(is_heavy),
                    "ZipCode": generate_zip(is_bad_zip, add_spaces=random.choice([True, False])),
                    "Recipient": f"Recipient_{pkg_counter}"
                })
                
            with open(os.path.join(current_dir, "batch_B.json"), "w") as f:
                json.dump(json_data, f, indent=2)
                
            # TXT file (pipe separated)
            txt_data = []
            txt_data.append("Package_ID|Weight|ZipCode|Recipient")
            for _ in range(random.randint(20, 50)):
                pkg_counter += 1
                pid = f"PKG-{pkg_counter}"
                is_heavy = random.random() < 0.15
                is_bad_zip = random.random() < 0.15
                is_cancelled = random.random() < 0.10
                
                if is_cancelled:
                    cancellations.add(pid)
                    
                row = f"{pid}|{generate_weight(is_heavy)}|{generate_zip(is_bad_zip, add_spaces=random.choice([True, False]))}|Recipient_{pkg_counter}"
                txt_data.append(row)
                
            with open(os.path.join(current_dir, "batch_C.txt"), "w") as f:
                f.write("\n".join(txt_data))

    # 3. Write Cancellations File
    with open(os.path.join(logs_dir, "cancellations.txt"), "w") as f:
        # Mix some fake/random IDs in cancellations to add noise
        noise_ids = [f"PKG-{random.randint(1000, 9999)}" for _ in range(50)]
        all_cancels = list(cancellations) + noise_ids
        random.shuffle(all_cancels)
        f.write("\n".join(all_cancels))

if __name__ == "__main__":
    build_env()
