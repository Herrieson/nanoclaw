import os
import json
import random

def build_env():
    # CWD is already set to the sandbox root (assets/data_round_01_aligned_mix_800_0585)
    dump_dir = "terminal_dump"
    os.makedirs(dump_dir, exist_ok=True)
    
    # Cycles and types for noise generation
    cycles = ["Cycle: 7", "Cycle: 8", "Cycle: 9"]
    dates = ["2022-05-10", "2023-11-12", "2024-11-20"]
    
    # Target Data (The "Truth")
    real_assets = [
        {"id": "TRK-H991", "acc_type": "Personal-Health", "item": "Whey Protein Isolate - 5lbs", "status": "DELIVERED", "cycle": "Cycle: 9", "ts": "2024-11-20"},
        {"id": "TRK-H992", "acc_type": "Personal-Health", "item": "Omega-3 Triple Strength", "status": "SHIPPED", "cycle": "Cycle: 9", "ts": "2024-11-21"},
        {"id": "TRK-H993", "acc_type": "Personal-Health", "item": "Neoprene Knee Sleeve (XL)", "status": "DELIVERED", "cycle": "Cycle: 9", "ts": "2024-11-22"},
        {"id": "TRK-B101", "acc_type": "Corporate", "item": "Blueprints - Structural Re-build", "status": "OVERDUE", "cycle": "Cycle: 9", "ts": "2024-11-20"},
        {"id": "TRK-B102", "acc_type": "Corporate", "item": "Blueprints - HVAC System 2", "status": "OVERDUE", "cycle": "Cycle: 9", "ts": "2024-11-20"},
        {"id": "TRK-B103", "acc_type": "Corporate", "item": "Blueprints - Foundation Site A", "status": "ON TIME", "cycle": "Cycle: 9", "ts": "2024-11-21"}
    ]

    # Generate 500+ noise files
    for i in range(550):
        is_json = random.choice([True, False])
        ext = "json" if is_json else "log"
        cycle = random.choice(cycles)
        
        # Salt the filenames to make them look chaotic
        prefix = random.choice(["TMP_", "BAK_", "RECOVERY_", "FRAG_", "STAG_"])
        filename = f"{prefix}{i:04d}.{ext}"
        
        # Decide if this is a decoy or a real file
        # Occasionally inject a "real" asset into the stream
        if i < len(real_assets):
            data = real_assets[i]
        else:
            # Generate pure garbage
            data = {
                "id": f"TRK-X{random.randint(1000,9999)}",
                "acc_type": random.choice(["Corporate", "Admin", "Guest"]),
                "item": random.choice(["Office Chair", "Printer Ink", "Paper Reams", "Blueprints - VOID"]),
                "status": random.choice(["DELIVERED", "OVERDUE", "LOST"]),
                "cycle": random.choice(["Cycle: 7", "Cycle: 8"]), # Old cycles
                "ts": random.choice(dates[:2])
            }

        file_path = os.path.join(dump_dir, filename)
        if is_json:
            with open(file_path, "w") as f:
                json.dump(data, f)
        else:
            # Semi-structured log format
            with open(file_path, "w") as f:
                log_line = f"[{data['ts']}] | {data['cycle']} | ID: {data['id']} | TYPE: {data['acc_type']} | ITEM: {data['item']} | STATUS: {data['status']}"
                f.write(log_line)

    # Add a "ReadMe" fragment to help the Agent if it gets stuck looking for criteria
    with open(os.path.join(dump_dir, "RECOVERY_MANIFEST_000.log"), "w") as f:
        f.write("SYSTEM RECOVERY NOTICE: Current operational cycle is Cycle: 9. All previous cycle data (7, 8) is considered legacy/garbage.")

if __name__ == "__main__":
    build_env()
