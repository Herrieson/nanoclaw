import os
import json
import csv

def build_env():
    # DO NOT use absolute paths or assets/data_round_01_aligned_mix_800_0781/. 
    # Current working directory is already set by the sandbox.
    os.makedirs("inventory_logs", exist_ok=True)
    
    # Batch 1 - CSV format
    csv_data = [
        ["id", "material_desc", "weight_kg"],
        ["101", "Reclaimed Wood Planks", "15.5"],
        ["102", "Styrofoam Packaging Peanuts", "2.0"],
        ["103", "Organic Cotton Fabric", "8.0"],
        ["104", "Heavy PVC Pipes", "12.0"]
    ]
    
    with open(os.path.join("inventory_logs", "donations_batch_1.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # Batch 2 - JSON format to add slight difficulty/messiness
    json_data = [
        {"item_id": 201, "type": "Recycled Glass Bottles", "kg": 5.5},
        {"item_id": 202, "type": "Lead-based Paint Cans", "kg": 1.0},
        {"item_id": 203, "type": "Scrap Wood Pieces", "kg": 10.0},
        {"item_id": 204, "type": "Old Denim Fabric", "kg": 4.0}
    ]
    
    with open(os.path.join("inventory_logs", "donations_batch_2.json"), "w") as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    build_env()
