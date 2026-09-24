import os
import json
import csv
import random

def build_env():
    random.seed(1197)
    
    os.makedirs("mezclas_archive/2023", exist_ok=True)
    os.makedirs("mezclas_archive/2022", exist_ok=True)
    os.makedirs("lab_results", exist_ok=True)

    wood_types = ["Oak", "Pine", "Walnut", "Mahogany", "Cherry", "cherry", "CHERRY", "Maple"]
    
    batches_2023 = []
    batches_2022 = []
    lab_results = []

    # Generate 2023 Data (The truth)
    for i in range(1, 601):
        batch_id = f"B23-{i:04d}"
        wood = random.choice(wood_types)
        vol = random.randint(10, 500)
        red_pct = random.randint(0, 30)
        blue_pct = random.randint(0, 10)
        
        batches_2023.append({"id": batch_id, "wood": wood, "vol": vol})
        lab_results.append({"batch_id": batch_id, "red_pigment_pct": red_pct, "blue_pigment_pct": blue_pct, "technician": "Julio"})

    # Generate 2022 Data (Decoys)
    for i in range(1, 201):
        batch_id = f"B22-{i:04d}"
        wood = random.choice(["Cherry", "Oak", "Pine"])
        vol = random.randint(10, 500)
        red_pct = random.randint(0, 30)
        
        batches_2022.append({"id": batch_id, "wood": wood, "vol": vol})
        lab_results.append({"batch_id": batch_id, "red_pigment_pct": red_pct, "blue_pigment_pct": 5, "technician": "Martin"})

    random.shuffle(batches_2023)
    random.shuffle(batches_2022)
    random.shuffle(lab_results)

    # Distribute 2023 data into months (01 to 12) and different formats
    chunk_size = len(batches_2023) // 12
    for month in range(1, 13):
        month_dir = f"mezclas_archive/2023/{month:02d}"
        os.makedirs(month_dir, exist_ok=True)
        
        start_idx = (month - 1) * chunk_size
        end_idx = start_idx + chunk_size if month < 12 else len(batches_2023)
        month_data = batches_2023[start_idx:end_idx]
        
        # Split into JSON, CSV, TXT
        json_data = month_data[:len(month_data)//3]
        csv_data = month_data[len(month_data)//3:2*len(month_data)//3]
        txt_data = month_data[2*len(month_data)//3:]
        
        with open(f"{month_dir}/records_A.json", "w", encoding="utf-8") as f:
            json.dump([{"batch_id": d["id"], "wood_type": d["wood"], "volume_l": d["vol"]} for d in json_data], f, indent=2)
            
        with open(f"{month_dir}/records_B.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "wood", "vol_liters"])
            for d in csv_data:
                writer.writerow([d["id"], d["wood"], d["vol"]])
                
        with open(f"{month_dir}/records_C.txt", "w", encoding="utf-8") as f:
            f.write("BatchID|Type|Liters\n")
            for d in txt_data:
                f.write(f"{d['id']}|{d['wood']}|{d['vol']}\n")

    # Distribute 2022 data
    with open("mezclas_archive/2022/old_log.json", "w", encoding="utf-8") as f:
        json.dump([{"batch_id": d["id"], "wood_type": d["wood"], "volume_l": d["vol"]} for d in batches_2022], f, indent=2)

    # Distribute Lab Results into scattered files
    lab_chunks = [lab_results[i:i + 100] for i in range(0, len(lab_results), 100)]
    for idx, chunk in enumerate(lab_chunks):
        if idx % 2 == 0:
            with open(f"lab_results/test_run_{idx}.json", "w", encoding="utf-8") as f:
                json.dump(chunk, f, indent=2)
        else:
            with open(f"lab_results/test_run_{idx}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["batch_id", "red_pigment_pct", "blue_pigment_pct", "technician"])
                for d in chunk:
                    writer.writerow([d["batch_id"], d["red_pigment_pct"], d["blue_pigment_pct"], d["technician"]])

if __name__ == "__main__":
    build_env()
