import os
import json
import random
import csv

def build_env():
    # 1. Create a fragmented contract structure
    os.makedirs("legacy_vault/contracts_v4_final/archives", exist_ok=True)
    approved_rates = {
        "Steel Horizon Corp": 125.50,
        "Bio-Hazard Remediation Ltd": 210.00,
        "Neon Grid Electrical": 95.00,
        "Waste-Land Logistics": 45.00,
        "Rad-Shield Construction": 180.00
    }
    
    # Split rates into fragmented JSON files
    for name, rate in approved_rates.items():
        slug = name.lower().replace(" ", "_")
        path = f"legacy_vault/contracts_v4_final/archives/contract_{slug}_fragment.json"
        with open(path, "w") as f:
            json.dump({"entity": name, "contract_terms": {"hourly_fixed": rate, "currency": "USD"}}, f)

    # 2. Create a messy work_logs directory with decoys
    os.makedirs("work_logs", exist_ok=True)
    
    # Data generation parameters
    contractors = list(approved_rates.keys())
    statuses = ["DRAFT", "PENDING", "FINAL", "VOID", "REJECTED"]
    
    # Generate 200+ files to force programmatic handling
    for i in range(250):
        # Determine if this is a "real" file or a decoy
        is_real = random.random() < 0.15  # Only 15% are valid "FINAL" logs
        contractor = random.choice(contractors)
        status = "FINAL" if is_real else random.choice([s for s in statuses if s != "FINAL"])
        
        # Add "FINAL" to filename occasionally as a clue, or hide it inside
        filename_tag = "_FINAL" if (is_real and random.random() > 0.5) else f"_tmp_{i}"
        file_ext = random.choice([".csv", ".txt", ".log"])
        filename = f"log_session_{i}{filename_tag}{file_ext}"
        
        hours = random.randint(1, 40)
        # Create overbilling scenario
        billed_rate = approved_rates[contractor]
        if is_real and contractor in ["Steel Horizon Corp", "Rad-Shield Construction"]:
            billed_rate += 25.0  # Attempted overbilling
            
        filepath = os.path.join("work_logs", filename)
        
        if file_ext == ".csv":
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metadata_Status", "Worker", "Hours", "Rate_Claimed"])
                writer.writerow([status, contractor, hours, billed_rate])
        elif file_ext == ".json": # Add some variety
             with open(filepath, "w") as f:
                json.dump({"status": status, "sub": contractor, "duration": hours, "rate": billed_rate}, f)
        else: # Semi-structured text
            with open(filepath, "w") as f:
                f.write(f"SESSION_START\nSTATUS: {status}\nCONTRACTOR: {contractor}\nHOURS_WORKED: {hours}\nCLAIMED_RATE: {billed_rate}\nSESSION_END")

    # Ensure at least one valid FINAL entry for each contractor exists so the task is solvable
    for i, contractor in enumerate(contractors):
        fname = f"certified_payout_submission_{i}_FINAL.csv"
        hours = 10 + i
        rate = approved_rates[contractor]
        if contractor in ["Steel Horizon Corp", "Rad-Shield Construction"]:
            rate += 50.0 # Clear overbilling
            
        with open(os.path.join("work_logs", fname), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metadata_Status", "Worker", "Hours", "Rate_Claimed"])
            writer.writerow(["FINAL", contractor, hours, rate])

if __name__ == "__main__":
    build_env()
