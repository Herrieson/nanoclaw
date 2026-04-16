import os
import json
import base64
import random
from datetime import datetime, timedelta

def create_environment():
    base_dir = "assets/data_121"
    logs_dir = os.path.join(base_dir, "sim_logs")
    os.makedirs(logs_dir, exist_ok=True)

    random.seed(42) # Ensure deterministic generation
    start_time = datetime(2023, 10, 24, 8, 0, 0)
    
    # 3 files
    for file_idx in range(1, 4):
        file_path = os.path.join(logs_dir, f"sim_run_00{file_idx}.log")
        with open(file_path, "w") as f:
            for i in range(20):
                # Increment time
                current_time = start_time + timedelta(minutes=random.randint(1, 15), seconds=random.randint(0, 59))
                start_time = current_time
                
                time_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Determine if anomaly
                is_anomaly = random.random() < 0.15 # 15% chance of anomaly
                
                if is_anomaly:
                    stress = round(random.uniform(85.1, 120.0), 2)
                    deflection = round(random.uniform(1.5, 3.0), 3)
                else:
                    stress = round(random.uniform(20.0, 84.9), 2)
                    deflection = round(random.uniform(0.01, 1.49), 3)
                    
                sensor_id = f"NODE-X{random.randint(100, 999)}"
                
                payload_dict = {
                    "sensor_id": sensor_id,
                    "stress_level": stress,
                    "deflection": deflection
                }
                
                payload_json = json.dumps(payload_dict)
                payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
                
                # Introduce some garbage logs that don't have payloads
                if random.random() < 0.1:
                    log_line = f"[{time_str}] [WARN] [SYSTEM-CORE] Dropped packet from {sensor_id}. Retrying...\n"
                else:
                    log_line = f"[{time_str}] [INFO] [TELEMETRY-ROUTINE] Data fetched successfully. RAW_PAYLOAD: {payload_b64} | STATUS: OK\n"
                
                f.write(log_line)

if __name__ == "__main__":
    create_environment()
    print("Environment built successfully at assets/data_121")
