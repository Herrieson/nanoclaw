import os
import csv
import json
import random

def build_env():
    # Set seed for reproducible wasteland generation
    random.seed(1089)
    
    # Core directories
    os.makedirs("reactor_data/registry", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Generate Reactor Registry (Noise & Valid mixed)
    reactors = []
    active_reactor_ids = set()
    for i in range(1, 101):
        r_id = f"R-{i:03d}"
        # 30% chance to be completely active and valid
        is_active = random.random() < 0.3
        
        status = "ONLINE" if (is_active or random.random() < 0.5) else "OFFLINE"
        cert = "VALID" if (is_active or random.random() < 0.4) else random.choice(["EXPIRED", "PENDING", "REVOKED"])
        
        # Enforce the logic: Active only if BOTH are true
        if is_active:
            status = "ONLINE"
            cert = "VALID"
            active_reactor_ids.add(r_id)
            
        reactors.append({
            "reactor_id": r_id,
            "installed_date": f"202{random.randint(0, 3)}-0{random.randint(1,9)}-15",
            "status": status,
            "certification": cert,
            "max_capacity": random.randint(1000, 5000)
        })
    
    with open("reactor_data/registry/master_registry.json", "w") as f:
        json.dump({"last_updated": "2023-10-27T08:00:00Z", "reactors": reactors}, f, indent=4)
        
    # Decoy registry
    with open("reactor_data/registry/deprecated_registry_v1.json", "w") as f:
        json.dump({"WARNING": "DO NOT USE", "reactors": [{"reactor_id": "R-999", "status": "ONLINE", "certification": "VALID"}]}, f)

    # 2. Generate Scattered Logs
    file_counter = 0
    batch_counter = 10000
    
    # We will create 150 files across different zones and weeks
    for zone in ["zone_alpha", "zone_beta", "zone_gamma", "zone_delta"]:
        for week in ["week_41", "week_42", "week_43"]:
            dir_path = f"reactor_data/logs/{zone}/{week}"
            os.makedirs(dir_path, exist_ok=True)
            
            # 10 to 15 files per directory
            num_files = random.randint(10, 15)
            for _ in range(num_files):
                file_counter += 1
                file_format = random.choice(["csv", "json", "log"])
                file_name = f"sensor_dump_{file_counter}.{file_format}"
                full_path = os.path.join(dir_path, file_name)
                
                # Generate 15-25 batches per file
                batches = []
                for _ in range(random.randint(15, 25)):
                    batch_counter += 1
                    b_id = f"B{batch_counter}"
                    # 50% chance to be an active reactor, 50% chance to be noise
                    r_id = random.choice(list(active_reactor_ids)) if random.random() < 0.5 else f"R-{random.randint(1, 100):03d}"
                    
                    temp = round(random.uniform(180.0, 240.0), 1)
                    weight = random.randint(1000, 5000)
                    # Flirt with the 15% threshold for green failures
                    recycled = int(weight * random.uniform(0.05, 0.30))
                    output = weight - random.randint(50, 200) # Waste is total - output
                    
                    batches.append({
                        "b_id": b_id, "r_id": r_id, "temp": temp, "weight": weight, "recycled": recycled, "output": output
                    })
                
                # Write to the specific format with DIFFERENT schemas
                if file_format == "csv":
                    with open(full_path, "w", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["batch_id", "reactor_id", "temp_c", "total_weight_kg", "recycled_content_kg", "output_product_kg"])
                        for b in batches:
                            writer.writerow([b["b_id"], b["r_id"], b["temp"], b["weight"], b["recycled"], b["output"]])
                            
                elif file_format == "json":
                    json_data = []
                    for b in batches:
                        json_data.append({
                            "batch_id": b["b_id"],
                            "reactor": b["r_id"],
                            "temperature": b["temp"],
                            "weight": b["weight"],
                            "recycled": b["recycled"],
                            "output": b["output"]
                        })
                    with open(full_path, "w") as f:
                        json.dump(json_data, f, indent=2)
                        
                elif file_format == "log":
                    with open(full_path, "w") as f:
                        for b in batches:
                            f.write(f"[BATCH] ID:{b['b_id']} | R_ID:{b['r_id']} | TEMP:{b['temp']} | MASS:{b['weight']} | RECYCLED_MASS:{b['recycled']} | YIELD:{b['output']}\n")

                # Generate Noise / Corruption files (.bak, .tmp)
                if random.random() < 0.2:
                    noise_ext = random.choice([".bak", ".tmp"])
                    noise_path = full_path + noise_ext
                    with open(noise_path, "w") as f:
                        if file_format == "csv":
                            f.write("batch_id,reactor_id,temp_c,total_weight_kg,recycled_content_kg,output_product_kg\n")
                            f.write(f"B99999,R-999,999.9,1000,0,1000\n") # Guaranteed failure if read
                        elif file_format == "json":
                            f.write('[{"batch_id": "B99999", "reactor": "R-999", "temperature": 999.9, "weight": 1000, "recycled": 0, "output": 1000}]')
                        else:
                            f.write(f"[BATCH] ID:B99999 | R_ID:R-999 | TEMP:999.9 | MASS:1000 | RECYCLED_MASS:0 | YIELD:1000\n")

if __name__ == "__main__":
    build_env()
