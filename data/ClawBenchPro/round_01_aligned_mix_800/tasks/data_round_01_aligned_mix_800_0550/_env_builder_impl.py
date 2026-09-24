import os
import json
import csv
import random

def build_env():
    # 1. Create Directories
    os.makedirs("communications", exist_ok=True)
    os.makedirs("compliance", exist_ok=True)
    
    for i in range(1, 8):
        if i == 7:
            os.makedirs(f"telemetry_data/day_{i}/insects", exist_ok=True)
            os.makedirs(f"telemetry_data/day_{i}/yields", exist_ok=True)
        else:
            os.makedirs(f"telemetry_data/day_{i}", exist_ok=True)

    # 2. Write Internal Memo (The Rules)
    memo_content = """MEMORANDUM
From: Declan, Ag Manager
To: Data Team
Subject: Pesticide Drift Protocol & Telemetry Crash

1. Plot Registration: Our sensors are still picking up the conventional farm next door (the CONV- prefix plots). DO NOT INCLUDE THEM in our yield or damage assessments. Only count plots listed in the `compliance/organic_registry.json` file.

2. Damage Thresholds: A plot is considered compromised by pesticide drift if:
   - The total number of beneficial insects (sum of 'ladybugs' and 'lacewings') drops BELOW 15.
   AND
   - The total pest index (sum of 'aphids', 'thrips', and 'mites') surges ABOVE 800.

3. Sunday Crash: The system crashed on Day 7 (Sunday). Use ONLY Day 7 data for your final assessment. Days 1-6 are just historical noise and their data is irrelevant for the current inventory. Because of the crash, Day 7's data is heavily fragmented into individual files. Watch out for weird string formatting in the yield text files.
"""
    with open("communications/internal_memo.txt", "w") as f:
        f.write(memo_content)

    # 3. Generate Plot IDs and Registry
    organic_plots = [f"ORG-{str(i).zfill(3)}" for i in range(1, 151)]
    conventional_plots = [f"CONV-{str(i).zfill(3)}" for i in range(1, 51)]
    all_plots = organic_plots + conventional_plots

    with open("compliance/organic_registry.json", "w") as f:
        json.dump(organic_plots, f, indent=4)

    # 4. Define Ground Truth for Day 7
    # Exactly 5 organic plots are compromised
    compromised_orgs = ["ORG-013", "ORG-042", "ORG-088", "ORG-105", "ORG-149"]
    
    # Generate historical noise (Days 1-6) - monolithic files
    for day in range(1, 7):
        insects_history = []
        yields_history = []
        for plot in all_plots:
            insects_history.append({
                "plot_id": plot,
                "ladybugs": random.randint(20, 100),
                "lacewings": random.randint(20, 100),
                "aphids": random.randint(10, 300),
                "thrips": random.randint(10, 300),
                "mites": random.randint(10, 300)
            })
            yields_history.append([plot, random.randint(1000, 2000)])
            
        with open(f"telemetry_data/day_{day}/insects_summary.json", "w") as f:
            json.dump(insects_history, f)
        
        with open(f"telemetry_data/day_{day}/yield_summary.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["plot_id", "est_yield"])
            writer.writerows(yields_history)

    # Generate fragmented Day 7 (The actual test data)
    for plot in all_plots:
        # Determine status
        is_compromised = plot in compromised_orgs
        
        # Determine stats
        if is_compromised:
            lb = random.randint(0, 5)
            lw = random.randint(0, 5)
            # Ensure total ben < 15
            while lb + lw >= 15:
                lb = random.randint(0, 5)
                lw = random.randint(0, 5)
                
            aph = random.randint(300, 500)
            thr = random.randint(300, 500)
            mit = random.randint(300, 500)
            # Ensure total pest > 800
        else:
            lb = random.randint(20, 100)
            lw = random.randint(20, 100)
            aph = random.randint(10, 200)
            thr = random.randint(10, 200)
            mit = random.randint(10, 200)
            
        insect_data = {
            "sensor_id": f"SENS-{random.randint(1000,9999)}",
            "plot_id": plot,
            "metrics": {
                "ladybugs": lb,
                "lacewings": lw,
                "aphids": aph,
                "thrips": thr,
                "mites": mit
            }
        }
        
        with open(f"telemetry_data/day_7/insects/sensor_{plot}.json", "w") as f:
            json.dump(insect_data, f, indent=2)

        # Yield Data formulation
        # For organic plots, yield = 1000 + integer part of ID, e.g., ORG-013 -> 1013
        # This makes the math deterministic for evaluation.
        if plot.startswith("ORG-"):
            val = int(plot.split("-")[1])
            y_val = 1000 + val
        else:
            y_val = random.randint(1000, 2000)
            
        # Format with comma to force string parsing
        y_str = f"{y_val:,}"
        
        # Write weird txt format
        with open(f"telemetry_data/day_7/yields/est_{plot}.txt", "w") as f:
            f.write(f"=== YIELD ESTIMATE ===\n")
            f.write(f"Plot ID   : {plot}\n")
            f.write(f"Yield     : {y_str} lbs\n")
            f.write(f"======================\n")

if __name__ == "__main__":
    build_env()
    # GROUND TRUTH CHEATSHEET (For Evaluator reference):
    # Total Organic plots: 150 (ORG-001 to ORG-150)
    # Yield formula: 1000 + X. 
    # Total sum of all 150 organic plots: Sum(1001 to 1150) = 161,325
    # Compromised plots: ORG-013, ORG-042, ORG-088, ORG-105, ORG-149
    # Compromised yields: 1013 + 1042 + 1088 + 1105 + 1149 = 5,397
    # Total Safe Yield: 161,325 - 5,397 = 155,928
    # Expected compromised_plots list: ["ORG-013", "ORG-042", "ORG-088", "ORG-105", "ORG-149"]
