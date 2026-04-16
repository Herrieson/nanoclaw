import os
import json
import csv
import random

def build_env():
    # Determine the target directory
    # Assuming script is in tasks/data_450/ and we want to write to assets/data_450/
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/data_450'))
    
    # Create main and subdirectories
    data_dir = os.path.join(base_dir, 'waste_data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. Generate Energy Data (JSON with some noise/invalid entries)
    energy_data = []
    total_valid_kwh = 0.0
    
    # Generate some valid and invalid cooler readings
    for i in range(1, 16):
        if i % 4 == 0:
            # Inject noise
            energy_data.append({
                "device_id": f"COOLER_{i:02d}",
                "status": "OFFLINE",
                "consumption_kwh": "N/A"
            })
        elif i == 7:
            energy_data.append({
                "device_id": f"COOLER_{i:02d}",
                "status": "ERROR",
                "consumption_kwh": None
            })
        else:
            val = round(random.uniform(10.5, 55.2), 1)
            total_valid_kwh += val
            energy_data.append({
                "device_id": f"COOLER_{i:02d}",
                "status": "ONLINE",
                "consumption_kwh": val
            })
            
    # To make verification deterministic, we'll force a specific total by overriding the last valid entry
    # Let's target exactly 345.6 kWh
    current_sum = sum([entry.get('consumption_kwh') for entry in energy_data if isinstance(entry.get('consumption_kwh'), (int, float))])
    diff = 345.6 - current_sum
    # Find a valid entry to adjust
    for entry in energy_data:
        if isinstance(entry.get('consumption_kwh'), (int, float)):
            entry['consumption_kwh'] = round(entry['consumption_kwh'] + diff, 1)
            break
            
    with open(os.path.join(data_dir, 'energy_meters.json'), 'w', encoding='utf-8') as f:
        json.dump({"site": "Store_450", "readings": energy_data}, f, indent=2)

    # 2. Generate Bin Logs (CSV)
    # Bin-004 will be the worst
    bins = ['BIN-001', 'BIN-002', 'BIN-003', 'BIN-004', 'BIN-005']
    log_entries = []
    
    for _ in range(200):
        b = random.choice(bins)
        # Weight in kg
        weight = round(random.uniform(0.1, 5.0), 2)
        
        # Determine contamination
        # Make BIN-004 have a higher chance of contamination
        if b == 'BIN-004':
            contam = random.random() > 0.3 # 70% chance
        else:
            contam = random.random() > 0.85 # 15% chance
            
        log_entries.append([f"2023-10-24T{random.randint(8,20):02d}:{random.randint(0,59):02d}:00Z", b, weight, str(contam)])
        
    # Ensure BIN-004 strictly has the most
    # Just artificially add a bunch to BIN-004
    for _ in range(30):
        log_entries.append([f"2023-10-24T21:{random.randint(0,59):02d}:00Z", 'BIN-004', 1.2, "True"])

    with open(os.path.join(data_dir, 'bin_logs.csv'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'bin_id', 'weight_kg', 'contamination_flag'])
        writer.writerows(log_entries)

    # Save the ground truth values for the verifier into a hidden file or just let verifier hardcode it
    # We will let verifier hardcode/expect 345.6 and BIN-004

if __name__ == '__main__':
    build_env()
    print("Environment for data_450 built successfully.")
