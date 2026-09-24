import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Base directories
    base_path = "production_archives"
    os.makedirs(f"{base_path}", exist_ok=True)
    os.makedirs("management/final_report", exist_ok=True)

    parts_list = ["Spindle_Assembly", "Servo_Motor", "Coolant_Pump", "Hydraulic_Valve", "Ball_Screw"]
    critical_machines = []
    
    # 1. Create a deep, noisy directory tree
    for i in range(15):
        subdir = f"{base_path}/sector_{i:02d}/logs/temp_cache"
        os.makedirs(subdir, exist_ok=True)
        
        # Add decoys (Gardening/Music/Old logs)
        with open(f"{subdir}/note_{i}.txt", "w") as f:
            f.write(random.choice(["Cải bẹ xanh needs more water.", "Dạ Cổ Hoài Lang is a masterpiece.", "Buy more fertilizer."]))

    # 2. Scatter real diagnostic files (Fragmentation)
    # Only 3 machines are actually CRITICAL
    target_machines = [
        {"id": "MAC-9901", "status": "CRITICAL", "part": "Spindle_Assembly"},
        {"id": "MAC-4502", "status": "CRITICAL", "part": "Servo_Motor"},
        {"id": "MAC-1108", "status": "CRITICAL", "part": "Ball_Screw"}
    ]
    
    # Generate 200 dummy files
    for j in range(200):
        m_id = f"MAC-{random.randint(1000, 8000)}"
        status = random.choice(["NORMAL", "WARNING", "OPTIMAL"])
        p = random.choice(parts_list)
        path = f"{base_path}/sector_{random.randint(0,14):02d}/logs/temp_cache/diag_{random.getrandbits(32):x}.json"
        with open(path, "w") as f:
            json.dump({"machine_id": m_id, "wear_level": status, "part_needed": p, "vibration_index": random.random()}, f)

    # Inject the 3 CRITICAL ones
    for m in target_machines:
        path = f"{base_path}/sector_{random.randint(0,14):02d}/logs/temp_cache/diag_{random.getrandbits(32):x}.json"
        with open(path, "w") as f:
            json.dump({"machine_id": m["id"], "wear_level": m["status"], "part_needed": m["part"]}, f)

    # 3. Fragmented & Conflicting Pricing Data (Multi-hop Logic)
    # Create multiple price fragment files with different dates
    price_fragments = [
        {"Spindle_Assembly": 800, "Servo_Motor": 1100, "date": "2023-01-01"}, # Old
        {"Spindle_Assembly": 950, "date": "2024-05-20"},                     # Latest for Spindle
        {"Servo_Motor": 1350, "date": "2024-06-15"},                        # Latest for Servo
        {"Ball_Screw": 500, "date": "2023-12-10"},                          # Old
        {"Ball_Screw": 620, "date": "2024-07-01"},                          # Latest for Ball_Screw
        {"Coolant_Pump": 300, "date": "2024-01-01"}
    ]
    
    for idx, frag in enumerate(price_fragments):
        p_path = f"{base_path}/sector_{random.randint(0,14):02d}/price_update_v{idx}.log"
        with open(p_path, "w") as f:
            json.dump(frag, f)

    # 4. Mass Distraction (Scale Simulation)
    for k in range(50):
        d_path = f"{base_path}/personal_backup_{k}.txt"
        with open(d_path, "w") as f:
            f.write("Vietnam gardening tips #" + str(k))

if __name__ == "__main__":
    build_env()
