import os
import json
import random
import csv

def build():
    # 1. Create a fragmented and deep directory structure
    archives_path = "archives"
    terminal_logs_path = "terminal_logs"
    os.makedirs(archives_path, exist_ok=True)
    os.makedirs(terminal_logs_path, exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 2. Scale Simulation: Generate fragmented manifests with decoys
    hubs = ["Seattle-NW", "Chicago-Midwest", "Dallas-South", "Atlanta-East", "Miami-SE", "Denver-Mountain", "Phoenix-SW", "Boston-NE"]
    batches = ["V1-Standard", "V2-Neon", "V3-Pro", "V1-Beta", "V2-Neon-Refurb"]
    
    # Target batch: V2-Neon
    # We will hide manifest data in scattered JSON and CSV fragments
    for i in range(50):
        sub_dir = os.path.join(archives_path, f"node_{i:03d}")
        os.makedirs(sub_dir, exist_ok=True)
        
        # Determine if this is a real manifest or a "VOID/LEGACY" decoy
        is_valid = random.random() > 0.4
        tag = "CURRENT" if is_valid else random.choice(["VOID", "LEGACY", "DRAFT"])
        year = 2024 if is_valid else random.randint(2018, 2023)
        
        file_ext = random.choice([".json", ".csv", ".txt"])
        file_path = os.path.join(sub_dir, f"manifest_sig_{i}{file_ext}")
        
        data = {
            "meta": {"tag": tag, "fiscal_year": year, "checksum": f"SHA-{random.randint(100,999)}"},
            "entries": [
                {
                    "hub": random.choice(hubs),
                    "batch": random.choice(batches),
                    "qty": random.randint(100, 1000),
                    "id": f"SHP-{random.randint(1000, 9999)}"
                } for _ in range(random.randint(1, 3))
            ]
        }
        
        if file_ext == ".json":
            with open(file_path, 'w') as f:
                json.dump(data, f)
        elif file_ext == ".csv":
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["hub", "batch", "qty", "status", "year"])
                for entry in data["entries"]:
                    writer.writerow([entry["hub"], entry["batch"], entry["qty"], tag, year])
        else:
            with open(file_path, 'w') as f:
                f.write(f"LOG SIG: {tag} | YEAR: {year}\n")
                for entry in data["entries"]:
                    f.write(f"SHIPMENT: {entry['hub']} RECEIVE {entry['batch']} COUNT {entry['qty']}\n")

    # 3. Information Fragmentation: Scatter feedback logs with noise
    feedback_pool = [
        "The heat is manageable. Comfort rating: 4. Visuals are 10/10.",
        "Stiff fabric. Comfort rating: 2. Not great for 12h shifts.",
        "Best vest yet! Comfort rating: 5. Love the LED integration.",
        "Too many wires. Comfort rating: 3. It's okay.",
        "Battery gets warm but it's cold here anyway. Comfort rating: 4.",
        "Average fit. Comfort rating: 3.",
        "Terrible ergonomics. Comfort rating: 1. My back hurts.",
        "Standard gear. Comfort rating: 3. No complaints."
    ]

    for j in range(100):
        # Create nested folders
        deep_dir = os.path.join(terminal_logs_path, f"sector_{j // 10}", f"session_{j % 10}")
        os.makedirs(deep_dir, exist_ok=True)
        
        is_human_feedback = random.random() > 0.7
        file_path = os.path.join(deep_dir, f"telemetry_{j:04d}.log")
        
        if is_human_feedback:
            # Buried in text
            rating_text = random.choice(feedback_pool)
            with open(file_path, 'w') as f:
                f.write(f"TIMESTAMP: 2024-05-12T{random.randint(10,20)}:00:00Z\n")
                f.write("SENSOR_DATA: [36.5, 36.7, 36.4, 38.2]\n")
                f.write(f"USER_REMARKS: {rating_text}\n")
                f.write("END_OF_SESSION\n")
        else:
            # Pure noise
            with open(file_path, 'w') as f:
                f.write(f"SYSTEM PING: {random.random()}\n")
                f.write("NO USER ATTACHED\n")

if __name__ == "__main__":
    build()
