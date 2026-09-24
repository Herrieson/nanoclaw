import os
import json
import random

def build_env():
    # 🚨 Generate environment purely in cwd
    random.seed(1300)
    
    # 1. Create directory structure
    base_dir = "project_alpha"
    subs_dir = os.path.join(base_dir, "sub_contractors")
    comp_dir = os.path.join(base_dir, "compliance")
    log_dir = os.path.join(base_dir, "logistics", "manifests")
    
    for d in [subs_dir, comp_dir, log_dir]:
        os.makedirs(d, exist_ok=True)

    # 2. Generate Compliance and Payroll Data
    safety_clearance = {}
    total_expected_payroll = 0.0 # for verification

    for i in range(1, 151): # 150 sub-contractors
        sub_id = f"sub_{i:03d}"
        # Random clearance
        is_cleared = random.choice([True, False, True]) # 66% chance of True
        safety_clearance[sub_id] = is_cleared
        
        # Create sub folder and timesheet
        sub_folder = os.path.join(subs_dir, sub_id)
        os.makedirs(sub_folder, exist_ok=True)
        
        timesheet_lines = ["WorkerID,Hours,Rate\n"]
        num_workers = random.randint(3, 12)
        
        for w in range(num_workers):
            worker_id = f"W_{random.randint(1000, 9999)}"
            # Avoid floating point precision issues by using halves or whole numbers
            hours = float(random.randint(10, 60)) + random.choice([0.0, 0.5])
            rate = float(random.randint(15, 45))
            
            timesheet_lines.append(f"{worker_id},{hours},{rate}\n")
            
            # Keep track of expected truth
            if is_cleared:
                effective_rate = max(rate, 25.0)
                total_expected_payroll += hours * effective_rate
                
        with open(os.path.join(sub_folder, "timesheet.csv"), "w", encoding="utf-8") as f:
            f.writelines(timesheet_lines)

    # Write safety clearance
    with open(os.path.join(comp_dir, "safety_clearance.json"), "w", encoding="utf-8") as f:
        json.dump(safety_clearance, f, indent=4)

    # 3. Generate Logistics Data
    items = ["Rebar", "Wood", "Bricks", "Sand", "Cement", "Rubber Cement", "Gravel", "Steel Beams"]
    statuses = ["RECEIVED", "CANCELLED", "PENDING", "REJECTED"]
    
    total_expected_cement = 0
    
    for day in range(1, 251): # 250 daily logs
        log_lines = []
        num_entries = random.randint(5, 20)
        
        for _ in range(num_entries):
            log_id = random.randint(10000, 99999)
            weight = random.randint(50, 3000)
            item = random.choice(items)
            status = random.choice(statuses)
            
            log_line = f"[Log {log_id}] Item -> {weight} lbs of {item} || Status -> {status}\n"
            log_lines.append(log_line)
            
            # Keep track of expected truth
            if item == "Cement" and status == "RECEIVED":
                total_expected_cement += weight

        with open(os.path.join(log_dir, f"day_{day:03d}_manifest.txt"), "w", encoding="utf-8") as f:
            f.writelines(log_lines)

if __name__ == "__main__":
    build_env()
