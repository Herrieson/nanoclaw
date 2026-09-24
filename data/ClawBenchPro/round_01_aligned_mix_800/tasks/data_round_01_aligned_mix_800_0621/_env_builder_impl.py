import os
import json

def build_env():
    # Note: Execution cwd is already set to the task's asset directory
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    approved_fertilizers = [
        "Kelp Meal", 
        "Bone Meal", 
        "Compost Tea", 
        "Alfalfa Meal", 
        "Fish Emulsion"
    ]
    
    with open("approved_fertilizers.txt", "w") as f:
        f.write("\n".join(approved_fertilizers) + "\n")
        
    logs = [
        {"field_id": "Grove_North", "soil_ph": 6.5, "fertilizer_applied": "Bone Meal", "moisture_pct": 45},
        {"field_id": "Grove_South", "soil_ph": 5.8, "fertilizer_applied": "Compost Tea", "moisture_pct": 50},
        {"field_id": "Grove_East", "soil_ph": 6.2, "fertilizer_applied": "Synthetic UAN-32", "moisture_pct": 38},
        {"field_id": "Grove_West", "soil_ph": 7.0, "fertilizer_applied": "Kelp Meal", "moisture_pct": 42},
        {"field_id": "Grove_Central", "soil_ph": 5.2, "fertilizer_applied": "Ammonium Nitrate", "moisture_pct": 55}
    ]
    
    for i, log in enumerate(logs):
        filename = os.path.join("records", f"log_batch_2023100{i+1}.json")
        with open(filename, "w") as f:
            json.dump(log, f, indent=2)

if __name__ == "__main__":
    build_env()
