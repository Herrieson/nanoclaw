import os
import json
import base64
import random
import csv

def build_env():
    # Fix the random seed to ensure the wasteland is deterministic for evaluation
    random.seed(1528)
    
    # Create fragmented directory structures
    os.makedirs("raw_feedback/logs", exist_ok=True)
    os.makedirs("raw_feedback/registry", exist_ok=True)
    
    # --- 1. Generate Registries (Decoys vs Truth) ---
    # Decoy 1: 2021 Registry (Wrong names for targets)
    with open("raw_feedback/registry/registry_2021.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["u_id", "name", "email"])
        writer.writerow(["U_101", "Zack Snyder", "zack@fake.com"])
        writer.writerow(["U_102", "Bruce Wayne", "bat@fake.com"])
        for i in range(100):
            writer.writerow([f"U_{200+i}", f"OldUser_{i}", f"old_{i}@x.com"])
            
    # Decoy 2: 2022 Draft Registry
    with open("raw_feedback/registry/registry_2022_DRAFT.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["u_id", "name", "email"])
        writer.writerow(["U_101", "Alice S.", "a@fake.com"])
        writer.writerow(["U_102", "Bob J.", "b@fake.com"])
        for i in range(100):
            writer.writerow([f"U_{300+i}", f"DraftUser_{i}", f"draft_{i}@x.com"])
        
    # TRUTH: FINAL 2023 Registry
    target_users = {
        "U_101": "Alice Smith",
        "U_102": "Bob Jones",
        "U_103": "Charlie Davis",
        "U_104": "Diana Prince",
        "U_105": "Evan Wright",
        "U_106": "Fiona Gallagher",
        "U_107": "George Miller", 
        "U_108": "Hannah Abbott"  
    }
    with open("raw_feedback/registry/registry_FINAL_2023.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["u_id", "name", "email"])
        for uid, name in target_users.items():
            writer.writerow([uid, name, f"{name.split()[0].lower()}@example.com"])
        for i in range(2000):
            writer.writerow([f"U_{1000+i}", f"User_{i}", f"user{i}@example.com"])

    # --- 2. Generate Logs (Targets, Decoys, and massive Noise) ---
    # Actual answers
    targets = [
        {"type": "feedback", "u_id": "U_101", "comment": "The wheelchair ramp is blocked. Terrible Accessibility."},
        {"type": "feedback", "u_id": "U_102", "comment": "More diversity in product lines please."},
        {"type": "feedback", "u_id": "U_103", "comment": "I loved the cultural diversity event!"},
        {"type": "feedback", "u_id": "U_104", "comment": "accessibility to the restrooms is lacking."},
        {"type": "feedback", "u_id": "U_105", "comment": "DIVERSITY is important."},
        {"type": "feedback", "u_id": "U_106", "comment": "The accessibility features on your app are great."}
    ]
    
    # Tricky decoys (Wrong types, should be ignored)
    decoys = [
        {"type": "sys_log", "u_id": "SYS", "comment": "Accessibility API failed to load on POS terminal 4."},
        {"type": "sys_log", "u_id": "SYS", "comment": "Diversity module exception 0x884 encountered."},
        {"type": "employee_review", "u_id": "U_107", "comment": "Great diversity in the workplace."},
        {"type": "feedback", "u_id": "U_108", "comment": "Prices are too high and lines are long."} # Right type, wrong keywords
    ]
    
    all_events = []
    
    # Generate 10,000 noise events to simulate scale
    words = ["good", "bad", "service", "store", "price", "quality", "staff", "clean", "slow", "fast", "lighting", "music"]
    for i in range(10000):
        t = random.choice(["feedback", "sys_log", "transaction"])
        uid = f"U_{random.randint(1000, 2999)}" if t == "feedback" else "SYS"
        comment = " ".join(random.choices(words, k=random.randint(3, 10)))
        all_events.append({"type": t, "u_id": uid, "comment": comment})
        
    # Merge and shuffle
    all_events.extend(targets)
    all_events.extend(decoys)
    random.shuffle(all_events)
    
    # Chunk into 200 files
    chunk_size = len(all_events) // 200 + 1
    chunks = [all_events[i:i + chunk_size] for i in range(0, len(all_events), chunk_size)]
    
    # Distribute files across nested directories with mixed formats
    for idx, chunk in enumerate(chunks):
        region = idx % 5
        store = (idx // 5) % 10
        dir_path = f"raw_feedback/logs/region_{region}/store_{store}"
        os.makedirs(dir_path, exist_ok=True)
        
        # All files are vaguely named .dat, but internal structure varies wildly
        fmt = random.choice(["json_array", "json_lines", "base64_lines"])
        file_path = f"{dir_path}/log_export_{idx}.dat"
        
        with open(file_path, "w", encoding="utf-8") as f:
            if fmt == "json_array":
                json.dump(chunk, f, indent=2)
            
            elif fmt == "json_lines":
                for item in chunk:
                    f.write(json.dumps(item) + "\n")
            
            elif fmt == "base64_lines":
                # Introduce corrupted Base64 lines to test Agent's robustness (try/except)
                if random.random() < 0.2:
                    f.write("ERR_LOG_CORRUPTED_SECTOR_0x00\n")
                
                for item in chunk:
                    json_str = json.dumps(item)
                    b64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
                    f.write(b64_str + "\n")
                
                if random.random() < 0.2:
                    f.write("===END_OF_TRANSMISSION_FATAL_ERR===\n")

if __name__ == "__main__":
    build_env()
