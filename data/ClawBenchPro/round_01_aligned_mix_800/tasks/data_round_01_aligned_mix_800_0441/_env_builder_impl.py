import os
import json
import random
import csv

def build_env():
    # 🚨 Execution context: cwd is assets/data_round_01_aligned_mix_800_0441/
    base_dir = "archive"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Create the Official Roster (Hidden in a deep path)
    roster_path = os.path.join(base_dir, "metadata/internal/club_registry")
    os.makedirs(roster_path, exist_ok=True)
    official_members = [
        "Ethan Miller", "Chloe Chen", "Marcus Thorne", "Sarah Jenkins", 
        "Leo Rodriguez", "Aria Vance", "Julian Foxtrot", "Naomi Watts"
    ]
    with open(os.path.join(roster_path, "roster_v2_final_FINAL.json"), "w") as f:
        json.dump({"year": 2023, "status": "active", "members": [{"name": m, "grade": random.randint(9, 12)} for m in official_members]}, f)
    
    # 2. Generate Mass Noise & Fragmented Volunteer Logs
    # We will create 1000 files. Only some contain [SESSION_2023_CHARITY].
    intruders = ["Dave Smith", "Unknown Person", "Pizza Hunter", "Lurker_99"]
    
    log_dirs = [os.path.join(base_dir, f"logs/terminal_{i}") for i in range(1, 6)]
    for d in log_dirs:
        os.makedirs(d, exist_ok=True)

    for i in range(1200):
        # Decide if this is a real log or a decoy
        is_real = random.random() < 0.1 # 10% chance to be a real 2023 log
        filename = f"log_fragment_{i:04d}.txt"
        target_dir = random.choice(log_dirs)
        
        with open(os.path.join(target_dir, filename), "w") as f:
            if is_real:
                f.write("[SESSION_2023_CHARITY]\n")
                # Randomly pick a member or intruder
                name = random.choice(official_members + intruders)
                hours = round(random.uniform(1.0, 5.0), 1)
                f.write(f"USER: {name}\nDURATION: {hours} hours\nSTATUS: VERIFIED")
            else:
                # Junk data
                f.write(f"[SESSION_OLD_DATA_2021]\nUSER: Ghost_User_{i}\nDURATION: 0.0\nSTATUS: ARCHIVED")

    # 3. Fragmented Sales Data (Semistructured)
    sales_path = os.path.join(base_dir, "finances/ledger_fragments")
    os.makedirs(sales_path, exist_ok=True)
    
    # Fragment 1: The Sales
    sales_data = [
        "ITEM: Sketchbook | QTY: 10 | PRICE: 15.00",
        "ITEM: Charcoal_Kit | QTY: 5 | PRICE: 20.00",
        "ITEM: Premium_Canvas | QTY: 2 | PRICE: 50.00",
        "--- DATA CORRUPTION ---",
        "ITEM: Watercolor_Set | QTY: 4 | PRICE: 30.00"
    ]
    with open(os.path.join(sales_path, "sales_day_1.csv"), "w") as f:
        f.write("\n".join(sales_data))

    # Fragment 2: The Adjustments (The "Pitfall")
    adjustments = [
        "REFUND: Sketchbook | AMT: -15.00 | REASON: Damaged",
        "ADJUSTMENT: Tax_Correction | AMT: -5.50",
        "DONATION_MATCH: Charity_Boost | AMT: 100.00"
    ]
    with open(os.path.join(sales_path, "adjustments.log"), "w") as f:
        f.write("\n".join(adjustments))

    # Add 500 empty/useless folders to increase search depth
    for j in range(50):
        os.makedirs(os.path.join(base_dir, f"garbage/temp_{j}"), exist_ok=True)

if __name__ == "__main__":
    build_env()
