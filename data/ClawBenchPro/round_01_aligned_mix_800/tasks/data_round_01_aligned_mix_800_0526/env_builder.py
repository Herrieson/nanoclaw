import os
import json
import random
import uuid

def build_env():
    # 🚨 Execution context: cwd is 'assets/data_round_01_aligned_mix_800_0526/'
    os.makedirs("archives/logs/2023", exist_ok=True)
    os.makedirs("archives/logs/2024/legacy", exist_ok=True)
    os.makedirs("archives/tmp/recovery", exist_ok=True)
    os.makedirs("registry/fragments", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Fragmented Registry (The Truth)
    authorized_names = ["Sarah Chen", "Michael Ross", "Elena Rodriguez", "David Kim", "Arjun Mehta", "Zoe Washburne"]
    for i, name in enumerate(authorized_names):
        chunk = {"rank": i, "id": f"V-{100+i}", "full_name": name, "status": "ACTIVE"}
        with open(f"registry/fragments/auth_part_{i}.json", "w") as f:
            json.dump(chunk, f)
    
    # Decoy Registry
    with open("registry/fragments/auth_part_deprecated.json", "w") as f:
        json.dump({"full_name": "Intruder Alert", "status": "EXPIRED"}, f)

    # 2. Scale Simulation & Fragmentation (Logs)
    # Target values to find:
    # Illegal volunteers: "Shadow_User", "Unknown_99", "Admin_Root"
    # Anomalous BP IDs: "BP-ERR-999", "BP-ERR-777"
    
    illegal_volunteers = ["Shadow_User", "Unknown_99", "Admin_Root"]
    all_logs = []
    
    # Generate 500+ records across different files
    for i in range(500):
        is_legal = random.random() > 0.2
        volunteer = random.choice(authorized_names) if is_legal else random.choice(illegal_volunteers)
        duration = random.randint(15, 120)
        bp = random.randint(110, 150)
        status = "COMPLETED" if random.random() > 0.1 else "FAILED"
        
        all_logs.append({
            "entry_id": str(uuid.uuid4())[:8],
            "operator": volunteer,
            "systolic_bp": bp,
            "duration_min": duration,
            "status": status
        })

    # Inject specific required anomalies
    all_logs.append({"entry_id": "BP-ERR-999", "operator": "Sarah Chen", "systolic_bp": 245, "duration_min": 10, "status": "COMPLETED"})
    all_logs.append({"entry_id": "BP-ERR-777", "operator": "Michael Ross", "systolic_bp": 210, "duration_min": 5, "status": "COMPLETED"})
    
    # Shuffle and split logs into multiple files and locations
    random.shuffle(all_logs)
    chunk_size = 60
    paths = [
        "archives/logs/2023/raw_batch_alpha.json",
        "archives/logs/2024/raw_batch_beta.json",
        "archives/logs/2024/legacy/old_backup.json",
        "archives/tmp/recovery/recovered_fragments.json",
        "archives/logs/2024/batch_final.json"
    ]
    
    for i, path in enumerate(paths):
        start = i * chunk_size
        end = start + chunk_size if i < len(paths)-1 else len(all_logs)
        with open(path, "w") as f:
            json.dump(all_logs[start:end], f, indent=2)

    # Add a lot of noise files
    for i in range(10):
        with open(f"archives/logs/2023/junk_{i}.txt", "w") as f:
            f.write("CORRUPTED DATA " * 100)

if __name__ == "__main__":
    build_env()
