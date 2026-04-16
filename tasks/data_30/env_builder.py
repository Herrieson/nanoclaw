import os
import json
import random
import uuid

def build_env():
    base_dir = "assets/data_30/lab_data"
    os.makedirs(base_dir, exist_ok=True)
    
    random.seed(42)
    
    # Generate ground truth parameters
    control_mean = 52.0
    treatment_mean = 41.5
    std_dev = 4.0
    
    all_data = []
    
    # Generate 120 valid records
    for _ in range(60):
        val = random.gauss(control_mean, std_dev)
        all_data.append({"id": str(uuid.uuid4())[:8], "group": "Control", "biomarker_x": round(val, 3)})
    for _ in range(60):
        val = random.gauss(treatment_mean, std_dev)
        all_data.append({"id": str(uuid.uuid4())[:8], "group": "Treatment", "biomarker_x": round(val, 3)})
        
    # Generate 20 corrupted/noise records
    for _ in range(10):
        all_data.append({"id": str(uuid.uuid4())[:8], "group": "Unknown", "biomarker_x": round(random.gauss(50, 10), 3)})
    for _ in range(10):
        all_data.append({"id": str(uuid.uuid4())[:8], "group": random.choice(["Control", "Treatment"])}) # missing biomarker
        
    random.shuffle(all_data)
    
    # Scatter the data into files
    chunk_size = 5
    chunks = [all_data[i:i + chunk_size] for i in range(0, len(all_data), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        if i % 2 == 0:
            # Save as JSON .tmp
            with open(os.path.join(base_dir, f"batch_record_{i}.tmp"), "w") as f:
                json.dump(chunk, f)
        else:
            # Save as pipe delimited .bak
            with open(os.path.join(base_dir, f"dump_{i}.bak"), "w") as f:
                f.write("patient_id|cohort|bx_level\n")
                for record in chunk:
                    p_id = record.get("id", "")
                    grp = record.get("group", "")
                    bx = record.get("biomarker_x", "")
                    f.write(f"{p_id}|{grp}|{bx}\n")
                    
    # Create an empty ground_truth helper file for the verification script
    ground_truth = {
        "expected_mean_diff": abs(control_mean - treatment_mean),
        "expected_significant": True
    }
    with open("assets/data_30/ground_truth.json", "w") as f:
        json.dump(ground_truth, f)

if __name__ == "__main__":
    build_env()
