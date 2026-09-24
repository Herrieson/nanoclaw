import os
import json
import pandas as pd

def build_env():
    # Create the inventory directory
    os.makedirs("inventory_logs", exist_ok=True)
    
    # Batch 1 - Excel format (Requires openpyxl)
    # This adds the "Binary file" barrier
    excel_data = {
        "id": ["EX-101", "EX-102", "EX-103"],
        "material_desc": ["Reclaimed Wood Planks", "Styrofoam Blocks", "High-Density PVC"],
        "weight_kg": [15.5, 2.0, 12.0]
    }
    df_excel = pd.DataFrame(excel_data)
    df_excel.to_csv(os.path.join("inventory_logs", "donations_batch_1.xlsx"), index=False)
    
    # Batch 2 - JSON format
    json_data = [
        {"item_id": "JS-201", "type": "Recycled Glass Bottles", "kg": 5.5},
        {"item_id": "JS-202", "type": "Industrial Coating Slag", "kg": 1.5}, # Toxic, needs scanning
        {"item_id": "JS-203", "type": "Scrap Wood Pieces", "kg": 10.0}
    ]
    with open(os.path.join("inventory_logs", "donations_batch_2.json"), "w") as f:
        json.dump(json_data, f, indent=4)

    # Batch 3 - CSV format with codes
    csv_content = [
        "id,material_desc,weight_kg",
        "CV-301,Organic Cotton Fabric,8.0",
        "CV-302,Old Denim Fabric,4.0",
        "CV-303,Lead-Lined Glass Case,3.0" # Toxic
    ]
    with open(os.path.join("inventory_logs", "donations_batch_3.csv"), "w") as f:
        f.write("\n".join(csv_content))

    # Create placeholder for skills documentation
    os.makedirs("skills", exist_ok=True)

if __name__ == "__main__":
    build_env()
