import os
import json
import csv
import random

def build_env():
    os.makedirs("patient_registry", exist_ok=True)
    os.makedirs("daily_logs", exist_ok=True)
    
    random.seed(42)
    
    doctors = ["Aris", "Smith", "Jones"]
    programs = ["Charity", "Private", "Medicaid", "Medicare"]
    
    # 1. Generate Patient Registry (Information Fragmentation & Lookup)
    for i in range(1, 1001):
        pid = f"P-{i:04d}"
        prog = random.choice(programs)
        with open(f"patient_registry/{pid}.json", "w") as f:
            json.dump({
                "patient_id": pid, 
                "program": prog, 
                "registration_year": "2023",
                "notes": "System migrated record."
            }, f)
            
    # 2. Generate Daily Logs (Scale, Noise, and Multi-format Fragmentation)
    for day in range(1, 31):
        date_str = f"2023-11-{day:02d}"
        day_dir = f"daily_logs/{date_str}"
        os.makedirs(day_dir, exist_ok=True)
        
        # A. CSV Files
        for c in range(3):
            csv_data = [["patient_id", "time", "unit", "doctor_name", "status"]]
            for _ in range(25):
                pid = f"P-{random.randint(1, 1000):04d}"
                unit = random.choice(["hrs", "mins"])
                time_val = round(random.uniform(0.5, 4.0), 2) if unit == "hrs" else random.randint(15, 120)
                doc = random.choice(doctors)
                status = random.choice(["finalized", "draft", "in_progress"])
                csv_data.append([pid, time_val, unit, doc, status])
            
            with open(f"{day_dir}/log_{c}.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
                
        # B. JSON Files
        for j in range(2):
            json_data = []
            for _ in range(20):
                pid = f"P-{random.randint(1, 1000):04d}"
                unit = random.choice(["hours", "minutes"])
                time_val = round(random.uniform(0.5, 4.0), 2) if unit == "hours" else random.randint(15, 120)
                doc = random.choice(doctors)
                is_draft = random.choice([True, False])
                json_data.append({
                    "uid": pid, 
                    "duration": time_val, 
                    "unit": unit, 
                    "doc": doc, 
                    "is_draft": is_draft
                })
            
            with open(f"{day_dir}/records_{j}.json", "w") as f:
                json.dump(json_data, f, indent=2)
                
        # C. Unstructured TXT Files ("Scribbles")
        with open(f"{day_dir}/scribbles.txt", "w") as f:
            for _ in range(15):
                pid = f"P-{random.randint(1, 1000):04d}"
                unit = random.choice(["h", "m"])
                time_val = round(random.uniform(0.5, 4.0), 2) if unit == "h" else random.randint(15, 120)
                doc = random.choice(doctors)
                status = random.choice(["[FINAL]", "[DRAFT]"])
                f.write(f"{status} | ID: {pid} | Time: {time_val} {unit} | Doc: {doc}\n")

if __name__ == "__main__":
    build_env()
