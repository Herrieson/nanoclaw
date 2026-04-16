import os
import random
import datetime
import json

def build_env():
    base_dir = "assets/data_04"
    logs_dir = os.path.join(base_dir, "machine_logs")
    os.makedirs(logs_dir, exist_ok=True)

    machines = ["Extruder-1", "Press-A", "Welder-2", "CNC-Alpha"]
    reasons = ["Overheating", "Material jam", "Calibration lost", "Power dip", "Sensor fault"]

    expected_defects = []
    
    # Set a fixed seed for reproducible environments if needed, though random is fine as long as truth is saved
    random.seed(42)

    # Generate logs over a 14 day period
    start_date = datetime.date(2023, 10, 1)
    
    for day_offset in range(14):
        date_obj = start_date + datetime.timedelta(days=day_offset)
        
        # Create messy folder structure
        folder_name = random.choice(["week_1", "week_2", "misc_logs", "supervisor_dump"])
        dir_path = os.path.join(logs_dir, folder_name)
        os.makedirs(dir_path, exist_ok=True)

        filename = os.path.join(dir_path, f"shift_log_{date_obj.strftime('%Y%m%d')}_{random.randint(100,999)}.txt")
        
        with open(filename, 'w') as f:
            # Add some header noise
            f.write(f"--- LOG START: {date_obj} ---\n")
            f.write("System check: OK\n\n")
            
            for _ in range(random.randint(15, 30)):
                time_str = f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                machine = random.choice(machines)
                
                # 15% chance of defect
                if random.random() < 0.15:
                    reason = random.choice(reasons)
                    
                    # Mix up date formats in the logs to test parsing
                    date_format_choice = random.choice(['%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y'])
                    date_str = date_obj.strftime(date_format_choice)
                    
                    # Varying log line formats
                    line_format = random.choice([
                        f"[{date_str} {time_str}] {machine} - Status: DEFECT - Reason: {reason}\n",
                        f"ERR | {date_str} | {time_str} | {machine} | Status: DEFECT | Reason: {reason}\n"
                    ])
                    
                    expected_defects.append({
                        "date": date_obj.strftime('%Y-%m-%d'), 
                        "machine": machine, 
                        "reason": reason
                    })
                    f.write(line_format)
                else:
                    date_str = date_obj.strftime('%Y-%m-%d')
                    f.write(f"[{date_str} {time_str}] {machine} - Status: OK - Units produced: {random.randint(50, 500)}\n")

    # Save the ground truth invisibly to help the verifier
    with open(os.path.join(base_dir, ".ground_truth.json"), "w") as f:
        json.dump(expected_defects, f)

if __name__ == "__main__":
    build_env()
