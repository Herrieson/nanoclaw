import os
import csv
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Set seed for reproducibility so the challenge has a deterministic answer
    random.seed(42)
    
    os.makedirs("registry", exist_ok=True)
    os.makedirs("records/seeds", exist_ok=True)
    os.makedirs("records/watering", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Generate Botanical Registry
    plants = {}
    csv_path = os.path.join("registry", "botanical_registry.csv")
    
    organic_names = ["Tomato", "Cucumber", "Pumpkin", "Carrot", "Lettuce", "Radish", "Kale", "Spinach", "Pea", "Bean"]
    chemical_names = ["GMO_Corn", "Pesticide_Soy", "Treated_Wheat", "Synthetic_Cotton", "Chem_Beet"]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Plant_ID", "Plant_Name", "Type", "Notes"])
        
        # Generate 150 Organic and 100 Chemical plants with unique IDs
        for i in range(1, 251):
            p_id = f"P_{i:04d}"
            if i <= 150:
                name = f"{random.choice(organic_names)}_{i}"
                p_type = "Organic"
            else:
                name = f"{random.choice(chemical_names)}_{i}"
                p_type = "Chemical"
            
            plants[p_id] = {"name": name, "type": p_type}
            writer.writerow([p_id, name, p_type, "N/A"])

    # 2. Generate Scattered Seed Deposits (High Fragmentation & Noise)
    years = ["2022", "2023"]
    months = [f"{m:02d}" for m in range(1, 13)]
    states = ["viable", "moldy", "eaten_by_birds", "lost"]
    
    for i in range(1500):
        year = random.choice(years)
        month = random.choice(months)
        folder_path = os.path.join("records", "seeds", year, month)
        os.makedirs(folder_path, exist_ok=True)
        
        p_id = random.choice(list(plants.keys()))
        qty = random.randint(5, 500)
        state = random.choice(states)
        
        file_name = f"deposit_{i:05d}.json"
        file_path = os.path.join(folder_path, file_name)
        
        data = {
            "transaction_id": f"TXN_{i}",
            "plant_id": p_id,
            "qty": qty,
            "state": state,
            "inspector": "Martha" if random.random() > 0.5 else "Teacher"
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
            
        # Noise: Generate .bak and .tmp copies with modified (invalid) numbers
        if random.random() < 0.3:
            bad_data = data.copy()
            bad_data["qty"] = qty * 10 # Trap if they read backups!
            with open(file_path + random.choice([".bak", ".tmp"]), "w", encoding="utf-8") as f:
                json.dump(bad_data, f)

    # 3. Generate Watering Logs (Time-series multi-hop logic)
    start_date = datetime(2022, 1, 1)
    # Create 400 random dates
    dates = [start_date + timedelta(days=random.randint(0, 700)) for _ in range(400)]
    dates.sort()
    
    # We group logs by date to simulate daily log files
    logs_by_date = {}
    for d in dates:
        d_str = d.strftime("%Y%m%d")
        if d_str not in logs_by_date:
            logs_by_date[d_str] = []
            
        # Each date gets 1 to 5 random updates
        for _ in range(random.randint(1, 5)):
            p_id = random.choice(list(plants.keys()))
            interval = random.randint(1, 14)
            # Add some natural noise text
            prefix = random.choice(["UPDATE: ", "  UPDATE: ", "Just a note, UPDATE: "])
            logs_by_date[d_str].append(f"{prefix}{p_id} -> {interval} days")
            
            # Edge Case Simulation: Multiple updates on the SAME day for the SAME plant
            # The prompt says the last one at the bottom of the file wins.
            if random.random() < 0.1:
                interval_override = random.randint(1, 14)
                logs_by_date[d_str].append(f"Wait, no! UPDATE: {p_id} -> {interval_override} days")
                
    for d_str, lines in logs_by_date.items():
        log_path = os.path.join("records", "watering", f"log_{d_str}.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("=== Garden Log Book ===\n")
            f.write(f"Date: {d_str}\n\n")
            # Inject noise lines
            f.write("Watered the entrance flowers.\n")
            f.write("Martha says we need more compost.\n")
            for line in lines:
                f.write(line + "\n")
                if random.random() < 0.2:
                    f.write("Saw a pretty butterfly today.\n")

if __name__ == "__main__":
    build_env()
