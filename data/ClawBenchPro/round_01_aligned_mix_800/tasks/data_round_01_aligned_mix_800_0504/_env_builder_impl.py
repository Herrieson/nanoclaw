import os
import json
import random
import csv

def build_env():
    # 🚨 Execution context: cwd is assets/data_round_01_aligned_mix_800_0504/
    
    # 1. Create the fragmented terminal dumps
    base_dir = "terminal_dumps"
    sub_folders = ["north_terminal", "south_terminal", "bar_terminal", "archive_v1", "backups_corrupted"]
    os.makedirs(base_dir, exist_ok=True)
    
    # Secret numbers for validation
    total_tips = 0.0
    
    for folder in sub_folders:
        path = os.path.join(base_dir, folder)
        os.makedirs(path, exist_ok=True)
        
        # Generate noise (Decoys)
        for i in range(50):
            noise_file = os.path.join(path, f"OLD_DATA_{random.randint(1000, 9999)}.log")
            with open(noise_file, "w") as f:
                f.write(f"DUMMY_DATA|{random.random()*100}|VOID\n")

        # Generate actual task data (Hidden in specific folders)
        if "terminal" in folder:
            week_path = os.path.join(path, "current_week")
            os.makedirs(week_path, exist_ok=True)
            
            for i in range(30):
                is_valid = random.choice([True, False, False]) # 1/3 valid ratio
                prefix = "TX_LIVE_" if is_valid else "TX_TEST_"
                status = "SETTLED" if is_valid else random.choice(["VOID", "FAILED", "PENDING"])
                tip = round(random.uniform(5.0, 50.0), 2)
                
                filename = f"{prefix}{random.randint(10000, 99999)}.json"
                file_path = os.path.join(week_path, filename)
                
                data = {
                    "tx_id": f"id_{i}_{folder}",
                    "amount": round(random.uniform(20, 200), 2),
                    "tip": tip if is_valid else (random.choice(["N/A", "0.0", "ERROR"]) if random.random() > 0.5 else tip),
                    "status": status,
                    "meta": {"timestamp": "2023-10-27", "cashier": "Maria"}
                }
                
                with open(file_path, "w") as f:
                    json.dump(data, f)
                
                if is_valid:
                    total_tips += tip

    # 2. Create Payroll Shards (Fragmentation)
    payroll_dir = "payroll_shards"
    os.makedirs(payroll_dir, exist_ok=True)
    
    # We'll split the hours into 5 fragments each
    boh_hours_total = 160.0
    foh_hours_total = 90.0
    
    for i in range(5):
        # BOH Shard
        with open(os.path.join(payroll_dir, f"boh_shard_{i}.txt"), "w") as f:
            f.write(f"DEPT: BOH | SHIFT_ID: {100+i} | HRS: {boh_hours_total/5}")
        # FOH Shard
        with open(os.path.join(payroll_dir, f"foh_shard_{i}.json"), "w") as f:
            json.dump({"dept": "FOH", "hours": foh_hours_total/5, "note": "verified"}, f)
            
    # Add decoy payroll shards
    with open(os.path.join(payroll_dir, "legacy_payroll.old"), "w") as f:
        f.write("DEPT: BOH | HRS: 99999 | STATUS: DISCARDED")

    # 3. Create manager_desk (Target)
    os.makedirs("manager_desk", exist_ok=True)

if __name__ == "__main__":
    build_env()
