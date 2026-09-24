import os
import json
import csv
import random

def build_env():
    random.seed(1330) # Ensure deterministic wasteland
    
    # 1. Create the inventory database dump
    os.makedirs("museum_exports", exist_ok=True)
    artifacts = []
    
    with open("museum_exports/inventory_2023.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Artifact_ID", "Acquisition_Date", "Origin", "Status", "Notes"])
        
        for i in range(1, 501):
            art_id = f"ART-{i:04d}"
            status = random.choice(["VERIFIED", "VERIFIED", "PENDING", "REJECTED", "LOST"])
            artifacts.append({"id": art_id, "status": status})
            writer.writerow([
                art_id, 
                f"202{random.randint(0,3)}-0{random.randint(1,9)}-1{random.randint(0,9)}",
                random.choice(["Meteorite", "Lunar", "Martian", "Unknown"]),
                status,
                "Needs review" if status == "PENDING" else ""
            ])
            
    # 2. Setup the raw data dumps directory
    base_dir = "raw_spectrometer_dumps"
    
    # Sarah's CSVs
    sarah_dir = os.path.join(base_dir, "sarah")
    os.makedirs(sarah_dir, exist_ok=True)
    for batch in range(1, 51):
        file_path = os.path.join(sarah_dir, f"batch_{batch:02d}.csv")
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["artifact_id", "weight_g", "size_cm3", "machine", "operator"])
            for _ in range(random.randint(10, 30)):
                art = random.choice(artifacts)["id"]
                machine = random.choice(["Alpha", "Beta", "Gamma"])
                # Add some noise: negative values, missing values
                mass = round(random.uniform(-5.0, 50.0), 2) if random.random() > 0.1 else ""
                vol = round(random.uniform(-2.0, 10.0), 2) if random.random() > 0.1 else ""
                writer.writerow([art, mass, vol, machine, "Sarah"])

    # Kevin's flat JSONs
    for week in range(1, 6):
        kevin_dir = os.path.join(base_dir, "kevin", f"week_{week}")
        os.makedirs(kevin_dir, exist_ok=True)
        for log in range(1, 15):
            file_path = os.path.join(kevin_dir, f"log_{log:03d}.json")
            
            # Inject a corrupted file occasionally
            if random.random() < 0.05:
                with open(file_path, "w") as f:
                    f.write('[{"item": "ART-0012", "machine": "Alpha", "m": 12.5, "v": ') # Cut off!
                continue
                
            data = []
            for _ in range(random.randint(5, 25)):
                art = random.choice(artifacts)["id"]
                machine = random.choice(["Alpha", "Beta", "Gamma"])
                mass = round(random.uniform(-5.0, 50.0), 2) if random.random() > 0.1 else None
                vol = round(random.uniform(-2.0, 10.0), 2) if random.random() > 0.1 else None
                data.append({
                    "item": art,
                    "machine": machine,
                    "m": mass,
                    "v": vol,
                    "notes": "looks good"
                })
            with open(file_path, "w") as f:
                json.dump(data, f)

    # Chad's nested JSONs
    chad_dir = os.path.join(base_dir, "chad")
    os.makedirs(chad_dir, exist_ok=True)
    for session in range(1, 60):
        file_path = os.path.join(chad_dir, f"session_{session:02d}.json")
        machine = random.choice(["Alpha", "Beta", "Gamma"]) # Machine is at file level for Chad!
        
        readings = []
        for _ in range(random.randint(10, 40)):
            art = random.choice(artifacts)["id"]
            mass = round(random.uniform(-5.0, 50.0), 2) if random.random() > 0.1 else None
            vol = round(random.uniform(-2.0, 10.0), 2) if random.random() > 0.1 else None
            readings.append({
                "id": art,
                "mass_g": mass,
                "volume_cm3": vol
            })
            
        with open(file_path, "w") as f:
            json.dump({
                "metadata": {
                    "spectrometer": machine,
                    "operator": "Chad",
                    "date": f"2023-11-{random.randint(1,30):02d}"
                },
                "data": readings
            }, f, indent=2)
            
    # Add some random junk files
    os.makedirs(os.path.join(base_dir, "backups"), exist_ok=True)
    with open(os.path.join(base_dir, "backups", "old_schema_draft.txt"), "w") as f:
        f.write("Hey guys, let's make sure we all use CSVs going forward. -Chad")

if __name__ == "__main__":
    build_env()
