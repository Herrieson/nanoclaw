import os
import json
import csv
import random

def build_env():
    # 🚨 Ensure the working directory is structured correctly
    os.makedirs('assay_runs', exist_ok=True)
    os.makedirs('subjects_registry', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    random.seed(42)

    # 1. Build Subjects Registry
    # Create 500 subject profiles. Mix of active humans, withdrawn humans, and mice.
    subjects_info = {}
    for i in range(1, 501):
        subj_id = f"SUBJ_{i:03d}"
        if i % 7 == 0:
            species = "Mus musculus"
            status = "Active"
        elif i % 13 == 0:
            species = "Homo sapiens"
            status = "Withdrawn"
        else:
            species = "Homo sapiens"
            status = "Active"
            
        profile = {
            "subject_id": subj_id,
            "species": species,
            "status": status,
            "age": random.randint(20, 60),
            "blood_type": random.choice(["A", "B", "AB", "O"])
        }
        subjects_info[subj_id] = profile
        
        with open(os.path.join('subjects_registry', f"{subj_id}_profile.json"), 'w') as f:
            json.dump(profile, f)

    # 2. Build Assay Runs (Machines: XT-9000, Omega-7, Alpha-3) (Dates: 2023-10-20 to 2023-10-25)
    machines = ["XT-9000", "Omega-7", "Alpha-3"]
    dates = [f"2023-10-{day}" for day in range(20, 26)]
    
    # We will distribute random data into CSV, JSON, and TXT files across these folders
    valid_human_subjects = [s for s, p in subjects_info.items() if p["species"] == "Homo sapiens" and p["status"] == "Active"]
    
    # Let's define our specific targets and decoys
    targets_and_decoys = [
        # Gold Standards (Top 3 Active Humans, placed in valid machines/dates)
        {"id": "SUBJ_051", "m": "Alpha-3", "d": "2023-10-20", "type": "json", "G": 110, "I": 2, "HR": 50}, # MEQ: 45.83
        {"id": "SUBJ_182", "m": "Omega-7", "d": "2023-10-23", "type": "txt", "G": 105, "I": 2.5, "HR": 55}, # MEQ: 38.50
        {"id": "SUBJ_333", "m": "Alpha-3", "d": "2023-10-25", "type": "csv", "G": 100, "I": 3, "HR": 60},   # MEQ: 33.33
        
        # Decoy 1: Mouse with INSANE MEQ (Must be filtered by registry)
        {"id": "SUBJ_007", "m": "Omega-7", "d": "2023-10-20", "type": "csv", "G": 150, "I": 1, "HR": 120},  # MEQ: 300
        
        # Decoy 2: Withdrawn Human with High MEQ (Must be filtered by registry)
        {"id": "SUBJ_013", "m": "Alpha-3", "d": "2023-10-24", "type": "json", "G": 120, "I": 2, "HR": 60},  # MEQ: 60.0
        
        # Decoy 3: Valid Human but in XT-9000 during failure weekend (Must be filtered by date/machine)
        {"id": "SUBJ_200", "m": "XT-9000", "d": "2023-10-21", "type": "txt", "G": 140, "I": 2, "HR": 60},   # MEQ: 70.0
        {"id": "SUBJ_201", "m": "XT-9000", "d": "2023-10-22", "type": "csv", "G": 160, "I": 2, "HR": 60},   # MEQ: 80.0
        
        # Decoy 4: Valid Human but has negative artifacts (Must be filtered by value logic)
        {"id": "SUBJ_222", "m": "Omega-7", "d": "2023-10-25", "type": "json", "G": 200, "I": -2, "HR": 60}
    ]
    
    # Generate random background data
    for m in machines:
        for d in dates:
            dir_path = os.path.join('assay_runs', m, d)
            os.makedirs(dir_path, exist_ok=True)
            
            # Prepare data containers for this folder
            csv_data = [["SubjectID", "Fasting_Glucose", "Insulin", "Resting_Heart_Rate"]]
            json_data = []
            txt_data = ["### AUTO-GENERATED MACHINE LOG ###\n"]
            
            # Add some random subjects
            for _ in range(10):
                s_id = random.choice(valid_human_subjects)
                G = random.randint(80, 100)
                I = random.randint(10, 20)
                HR = random.randint(60, 80)
                
                # Randomly inject dirty data
                if random.random() < 0.1: G = "NaN"
                if random.random() < 0.1: I = -5
                
                assign_type = random.choice(["csv", "json", "txt"])
                
                if assign_type == "csv":
                    csv_data.append([s_id, G, I, HR])
                elif assign_type == "json":
                    json_data.append({"subject_id": s_id, "fasting_glucose": G, "insulin": I, "resting_heart_rate": HR})
                else:
                    txt_data.append(f"[INFO] 08:00 Target {s_id} observed: FastingGlucose={G}, Insulin={I}, RestingHeartRate={HR}\n")
            
            # Inject targets and decoys if they match this machine and date
            for td in targets_and_decoys:
                if td["m"] == m and td["d"] == d:
                    if td["type"] == "csv":
                        csv_data.append([td["id"], td["G"], td["I"], td["HR"]])
                    elif td["type"] == "json":
                        json_data.append({"subject_id": td["id"], "fasting_glucose": td["G"], "insulin": td["I"], "resting_heart_rate": td["HR"]})
                    elif td["type"] == "txt":
                        txt_data.append(f"[INFO] 09:30 Target {td["id"]} observed: FastingGlucose={td['G']}, Insulin={td['I']}, RestingHeartRate={td['HR']}\n")

            # Write files
            with open(os.path.join(dir_path, "batch_results.csv"), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
                
            with open(os.path.join(dir_path, "telemetry.json"), 'w') as f:
                json.dump(json_data, f, indent=2)
                
            # Add some completely malformed noise to txt
            txt_data.append("[ERROR] 23:59 Sensor timeout. FastingGlucose=NaN, Insulin=NaN, RestingHeartRate=0\n")
            with open(os.path.join(dir_path, "sensor_log.txt"), 'w') as f:
                f.writelines(txt_data)

if __name__ == '__main__':
    build_env()
