import os
import csv
import tarfile
import random

def create_env():
    # Define paths
    base_dir = "assets/data_499/workspace"
    os.makedirs(base_dir, exist_ok=True)
    
    archive_path = os.path.join(base_dir, "logs_backup.tar.gz")
    
    # Temporary directory for building logs
    temp_dir = "assets/data_499/temp_logs"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate Normal Batches
    for i in range(1, 15):
        batch_id = f"BATCH-{1000+i}-ALPHA"
        filepath = os.path.join(temp_dir, f"sensor_dump_{batch_id}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Batch_ID", "Temperature_C", "Pressure_PSI", "Agitator_RPM"])
            for t in range(50):
                # Normal temp is around 90-100
                temp = round(random.uniform(90.0, 101.5), 1)
                # Ensure we never accidentally trigger the anomaly
                if temp >= 102.5:
                    temp = 101.0
                pressure = round(random.uniform(30.0, 40.0), 2)
                rpm = random.randint(110, 130)
                writer.writerow([f"10:{t:02d}:00", batch_id, temp, pressure, rpm])

    # Generate the Faulty Batch
    faulty_batch_id = "BATCH-882-OMEGA"
    faulty_filepath = os.path.join(temp_dir, f"sensor_dump_{faulty_batch_id}.csv")
    with open(faulty_filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Batch_ID", "Temperature_C", "Pressure_PSI", "Agitator_RPM"])
        for t in range(50):
            if 20 <= t <= 23:
                # 4 consecutive readings >= 102.5
                temp = round(random.uniform(102.6, 104.5), 1)
                # Hardcoded specific pressures so the average is deterministic
                pressures = [45.20, 46.10, 45.80, 47.00]
                pressure = pressures[t - 20]
            else:
                temp = round(random.uniform(90.0, 101.5), 1)
                pressure = round(random.uniform(30.0, 40.0), 2)
            rpm = random.randint(110, 130)
            writer.writerow([f"11:{t:02d}:00", faulty_batch_id, temp, pressure, rpm])

    # Create tar.gz archive
    with tarfile.open(archive_path, "w:gz") as tar:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                tar.add(full_path, arcname=file)

    # Cleanup temp directory
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(temp_dir)

if __name__ == "__main__":
    create_env()
