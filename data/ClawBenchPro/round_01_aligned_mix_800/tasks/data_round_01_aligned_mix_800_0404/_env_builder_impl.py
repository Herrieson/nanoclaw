import os
import json
import csv
import random

def build_env():
    # Set random seed for reproducibility
    random.seed(42)

    os.makedirs('lab_archive/runs', exist_ok=True)
    os.makedirs('lab_archive/equipment_manuals', exist_ok=True)
    os.makedirs('lab_archive/qc_reports/daily', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    # 1. Create equipment manuals (Thresholds)
    specs = {
        "legacy_machines": {
            "Nexus-9": {"min_rfu": 100, "max_rfu": 500},
            "OptiMax-3": {"min_rfu": 50, "max_rfu": 1000}
        },
        "current_machines": {
            "Spectra-V": {"min_rfu": 200, "max_rfu": 800},
            "QuantStudio-Pro": {"min_rfu": 500, "max_rfu": 1500}
        }
    }
    with open('lab_archive/equipment_manuals/calibration_specs.json', 'w') as f:
        json.dump(specs, f, indent=4)

    # 2. Create QC contamination list
    contaminated_samples = set()
    for _ in range(300):
        contaminated_samples.add(f"SMP-{random.randint(10000, 99999)}")
    
    with open('lab_archive/qc_reports/daily/contamination_list.txt', 'w') as f:
        f.write("CONFIDENTIAL - CONTAMINATED SAMPLE IDs DO NOT USE\n")
        f.write("===============================================\n")
        for cid in contaminated_samples:
            f.write(f"{cid}\n")
            
    # Add some decoy txt files in qc_reports
    for i in range(5):
        with open(f'lab_archive/qc_reports/daily/sensor_log_{i}.txt', 'w') as f:
            f.write("Sensor temp normal.\nHumidity 45%.\n")

    # 3. Generate massive runs
    machines = ["Nexus-9", "OptiMax-3", "Spectra-V", "QuantStudio-Pro"]
    experiments = ["in vitro assays", "cell culture prep", "in vivo metabolic", "protein synthesis"]
    
    total_valid = 0
    sum_valid = 0.0

    # 200 runs
    for run_idx in range(1, 201):
        run_dir = f'lab_archive/runs/run_{run_idx:03d}'
        os.makedirs(run_dir, exist_ok=True)
        
        # Determine metadata
        machine = random.choice(machines)
        experiment = random.choice(experiments)
        
        metadata = {
            "operator": "Dr. Levin",
            "timestamp": f"2023-10-{random.randint(1, 31):02d}T10:00:00Z",
            "machine": machine,
            "experiment_type": experiment
        }
        with open(os.path.join(run_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
            
        # Generate data file (CSV)
        data_file = os.path.join(run_dir, 'readings.csv')
        with open(data_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sample_id', 'rfu_value', 'cycle_count'])
            
            # Each run has 20-50 samples
            num_samples = random.randint(20, 50)
            for _ in range(num_samples):
                sample_id = f"SMP-{random.randint(10000, 99999)}"
                # Mix of valid and invalid RFU values
                rfu = round(random.uniform(-100.0, 1500.0), 2)
                writer.writerow([sample_id, rfu, random.randint(30, 40)])
                
                # Logic check for the specific requirement
                if machine == "Spectra-V" and experiment == "in vivo metabolic":
                    if sample_id not in contaminated_samples:
                        if 200 <= rfu <= 800:
                            total_valid += 1
                            sum_valid += rfu

    # Create a decoy folder to confuse
    os.makedirs('lab_archive/legacy_data', exist_ok=True)
    for _ in range(10):
        with open(f'lab_archive/legacy_data/old_batch_{random.randint(1,99)}.csv', 'w') as f:
            f.write("sample_id,rfu\nOLD-1,500\nOLD-2,600\n")

if __name__ == "__main__":
    build_env()
