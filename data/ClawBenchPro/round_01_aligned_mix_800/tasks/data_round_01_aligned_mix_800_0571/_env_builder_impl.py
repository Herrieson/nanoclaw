import os
import json
import csv
import random

def build_env():
    random.seed(42)
    
    # 1. Create Directories
    os.makedirs("config_server/zones_sync", exist_ok=True)
    os.makedirs("warehouse_scans", exist_ok=True)
    os.makedirs("customer_support/tickets", exist_ok=True)
    
    # 2. Generate Mapping Truth and Noise
    correct_mapping = {}
    regions = ["TEXAS_CORE", "TEXAS_NORTH", "OKLAHOMA_SOUTH", "NEW_MEXICO_EAST"]
    statuses = ["ACTIVE", "ARCHIVED", "DEPRECATED", "DRAFT"]
    zones = ["Alpha-Transit", "Beta-Transit", "Gamma-Transit", "Delta-Transit", "Echo-Transit"]
    
    # Generate exactly 10 valid active TEXAS_CORE mapping files (100 zip codes total)
    valid_zips = [str(78000 + i) for i in range(100)]
    random.shuffle(valid_zips)
    
    file_index = 0
    for i in range(10):
        chunk = valid_zips[i*10 : (i+1)*10]
        local_map = {z: random.choice(zones) for z in chunk}
        correct_mapping.update(local_map)
        
        file_data = {
            "metadata": {"region": "TEXAS_CORE", "status": "ACTIVE", "version": f"1.{i}"},
            "mapping": local_map
        }
        with open(f"config_server/zones_sync/sync_node_{file_index}_tx.json", "w") as f:
            json.dump(file_data, f, indent=2)
        file_index += 1
        
    # Generate 50 noise mapping files
    for _ in range(50):
        region = random.choice(regions)
        status = random.choice(statuses)
        if region == "TEXAS_CORE" and status == "ACTIVE":
            status = "ARCHIVED" # Prevent accidental valid overlaps
            
        noise_zips = [str(random.randint(70000, 79999)) for _ in range(5)]
        noise_map = {z: random.choice(zones) for z in noise_zips}
        file_data = {
            "metadata": {"region": region, "status": status, "version": f"0.{random.randint(1,9)}"},
            "mapping": noise_map
        }
        with open(f"config_server/zones_sync/sync_node_{file_index}_noise.json", "w") as f:
            json.dump(file_data, f, indent=2)
        file_index += 1

    # 3. Generate Warehouse Scans (Package -> Zip Code)
    packages = []
    for i in range(2500):
        packages.append({
            "package_id": f"PKG-{10000 + i}",
            "destination_zip": random.choice(valid_zips),
            "weight": round(random.uniform(0.5, 20.0), 2)
        })
    
    # Scatter scans into date directories
    for day in range(1, 15):
        day_str = f"2023-11-{day:02d}"
        os.makedirs(f"warehouse_scans/{day_str}", exist_ok=True)
        
        day_packages = packages[(day-1)*150 : day*150]
        if not day_packages:
            continue
            
        with open(f"warehouse_scans/{day_str}/morning_shift.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["package_id", "destination_zip", "weight", "scan_time"])
            writer.writeheader()
            for p in day_packages[:75]:
                writer.writerow({**p, "scan_time": f"08:{random.randint(10,59)} AM"})
                
        with open(f"warehouse_scans/{day_str}/evening_shift.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["package_id", "destination_zip", "weight", "scan_time"])
            writer.writeheader()
            for p in day_packages[75:]:
                writer.writerow({**p, "scan_time": f"06:{random.randint(10,59)} PM"})

    # 4. Generate Tickets (Mismatched and Correct)
    tickets = []
    # Pick 800 packages to have tickets
    ticket_packages = random.sample(packages, 800)
    
    for i, p in enumerate(ticket_packages):
        actual_zip = p["destination_zip"]
        correct_zone = correct_mapping[actual_zip]
        
        # 300 wrong zones, 500 correct zones
        if i < 300:
            wrong_zones = [z for z in zones if z != correct_zone]
            assigned_zone = random.choice(wrong_zones)
        else:
            assigned_zone = correct_zone
            
        tickets.append({
            "ticket_id": f"TX-TKT-{5000 + i}",
            "package_id": p["package_id"],
            "assigned_zone": assigned_zone,
            "issue_code": f"ERR-{random.randint(1, 5)}"
        })
        
    random.shuffle(tickets)
    
    # Scatter tickets into CSV and JSON files randomly in customer_support/tickets/
    chunk_size = 50
    for i in range(0, len(tickets), chunk_size):
        chunk = tickets[i:i+chunk_size]
        if i % 2 == 0:
            with open(f"customer_support/tickets/batch_{i}.json", "w") as f:
                json.dump(chunk, f, indent=2)
        else:
            with open(f"customer_support/tickets/batch_{i}.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ticket_id", "package_id", "assigned_zone", "issue_code"])
                writer.writeheader()
                writer.writerows(chunk)

if __name__ == "__main__":
    build_env()
