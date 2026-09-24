import os
import json
import random

def build_env():
    # Setup base directories
    os.makedirs("archive/fragments/nodes", exist_ok=True)
    os.makedirs("archive/policies/current", exist_ok=True)
    os.makedirs("archive/policies/deprecated", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Obfuscate the Approved List
    # Place multiple versions, only the one in 'current' with a specific header is valid
    with open("archive/policies/deprecated/fertilizer_v1.txt", "w") as f:
        f.write("Chemical-X\nSynthetic-A\n")
    
    # The 'True' policy
    approved = ["Kelp Meal", "Bone Meal", "Compost Tea", "Alfalfa Meal", "Fish Emulsion", "Worm Castings"]
    with open("archive/policies/current/registry_final.txt", "w") as f:
        f.write("### ECO-CERTIFIED TREATMENT REGISTRY ###\n")
        f.write("Status: Active\n")
        f.write("\n".join(approved))

    # 2. Generate the "Wasteland" of data
    fields = [
        {"id": "Grove_Alpha", "ph": 6.8, "fert": "Kelp Meal", "status": "Final"},
        {"id": "Grove_Beta", "ph": 5.4, "fert": "Worm Castings", "status": "Final"}, # Violation: Low pH
        {"id": "Grove_Gamma", "ph": 6.2, "fert": "Ammonium Sulfate", "status": "Final"}, # Violation: Forbidden fert
        {"id": "Grove_Delta", "ph": 4.9, "fert": "Anhydrous Ammonia", "status": "Final"}, # Violation: Both
        {"id": "Grove_Epsilon", "ph": 7.1, "fert": "Fish Emulsion", "status": "Final"},
        {"id": "Grove_Zeta", "ph": 6.0, "fert": "Bone Meal", "status": "Final"}
    ]

    # Create hundreds of noise files
    for i in range(300):
        noise_id = f"Temp_{random.randint(1000, 9999)}"
        file_path = f"archive/fragments/nodes/fragment_{i:03d}.log"
        with open(file_path, "w") as f:
            if random.random() > 0.5:
                f.write(f"SYSTEM_CHECK: Sensor {noise_id} - OK\n")
            else:
                json.dump({"temp_id": noise_id, "reading": random.uniform(0, 10), "tag": "obsolete"}, f)

    # Inject the real data fragmented and disguised
    for field in fields:
        # Fragment 1: The pH data (JSON)
        ph_path = f"archive/fragments/nodes/report_ph_{field['id']}_001.json"
        with open(ph_path, "w") as f:
            json.dump({"field_id": field['id'], "soil_ph": field['ph'], "type": "soil_report", "meta": field['status']}, f)
        
        # Fragment 2: The Treatment data (Text/Log style)
        fert_path = f"archive/fragments/nodes/log_treatment_{field['id']}_002.txt"
        with open(fert_path, "w") as f:
            f.write(f"TIMESTAMP: 2023-10-12T10:00:00Z\n")
            f.write(f"ID: {field['id']}\n")
            f.write(f"TREATMENT_APPLIED: {field['fert']}\n")
            f.write(f"STATUS: {field['status']}\n")

    # Add decoys: same Field IDs but status 'Draft' or 'Error'
    for field in fields:
        decoy_path = f"archive/fragments/nodes/backup_{field['id']}_old.json"
        with open(decoy_path, "w") as f:
            json.dump({"field_id": field['id'], "soil_ph": 7.0, "status": "Draft/Corrupted"}, f)

if __name__ == "__main__":
    build_env()
