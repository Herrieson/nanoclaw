import os
import json
import csv
import random

def build_env():
    # Directories
    os.makedirs("project_planning", exist_ok=True)
    os.makedirs("mill_data/codes", exist_ok=True)
    os.makedirs("mill_data/archive", exist_ok=True)
    
    # Generate material dictionary
    mat_dict = {
        "WO-01": "White Oak",
        "RO-02": "Red Oak",
        "MA-03": "Maple",
        "PI-04": "Pine",
        "WA-05": "Walnut",
        "CH-06": "Cherry"
    }
    with open("mill_data/codes/material_dictionary.json", "w") as f:
        json.dump(mat_dict, f, indent=4)
        
    random.seed(42) # For reproducibility
    materials = list(mat_dict.keys())
    conditions = ["Usable", "Warped", "Split", "Rotten", "Wet", "Knotted"]
    
    def generate_record(idx):
        mat = random.choice(materials)
        cond = random.choice(conditions)
        t = random.choice([1.0, 1.5, 2.0, 2.5, 3.0])
        w = random.choice([4.0, 6.0, 8.0, 10.0, 12.0])
        l = random.choice([24.0, 36.0, 48.0, 60.0, 72.0, 84.0, 96.0, 120.0])
        return f"ITEM-{idx:05d}", mat, t, w, l, cond

    item_counter = 1
    
    # Generate active logs
    for month in range(1, 4):
        for week in range(1, 5):
            dir_path = f"mill_data/inventory_logs/month_{month:02d}/week_{week:02d}"
            os.makedirs(dir_path, exist_ok=True)
            
            # Generate 1 CSV file
            csv_data = []
            for _ in range(random.randint(20, 50)):
                csv_data.append(generate_record(item_counter))
                item_counter += 1
            with open(f"{dir_path}/shipment_{random.randint(100,999)}.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Item_ID", "Material_Code", "Thickness_in", "Width_in", "Length_in", "Condition"])
                writer.writerows(csv_data)
                
            # Generate 1 JSON file
            json_data = []
            for _ in range(random.randint(20, 50)):
                i_id, mat, t, w, l, cond = generate_record(item_counter)
                json_data.append({
                    "ref_id": i_id,
                    "mat": mat,
                    "dims_inches": f"{t}x{w}x{l}",
                    "status": cond
                })
                item_counter += 1
            with open(f"{dir_path}/batch_{random.randint(100,999)}.json", "w") as f:
                json.dump(json_data, f, indent=2)
                
            # Generate 1 TXT log file
            txt_data = ""
            for _ in range(random.randint(20, 50)):
                i_id, mat, t, w, l, cond = generate_record(item_counter)
                txt_data += f"[RECORD] ID:{i_id} | MatCode:{mat} | Size(in):{t}x{w}x{l} | State:{cond}\n"
                item_counter += 1
            with open(f"{dir_path}/notes_{random.randint(100,999)}.log", "w") as f:
                f.write(txt_data)
                
            # Generate NOISE / DECOYS
            # .bak or .tmp files (should be ignored)
            bad_data = f"[RECORD] ID:ITEM-99999 | MatCode:WO-01 | Size(in):100x100x100 | State:Usable\n"
            ext = random.choice([".bak", ".tmp"])
            with open(f"{dir_path}/draft_v1{ext}", "w") as f:
                f.write(bad_data)

    # Generate ARCHIVE trap (should be ignored)
    for _ in range(3):
        archive_data = ""
        for _ in range(100):
            # Giant trap of usable white oak
            archive_data += f"[RECORD] ID:TRAP-{item_counter} | MatCode:WO-01 | Size(in):2x12x96 | State:Usable\n"
            item_counter += 1
        with open(f"mill_data/archive/archived_stock_{random.randint(10,99)}.log", "w") as f:
            f.write(archive_data)

if __name__ == "__main__":
    build_env()
