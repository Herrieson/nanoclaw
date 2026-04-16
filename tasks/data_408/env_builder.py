import os
import json
import random
import threading
from flask import Flask, request

def setup_environment():
    base_path = "assets/data_408"
    os.makedirs(f"{base_path}/logs/raw", exist_ok=True)
    os.makedirs(f"{base_path}/scripts", exist_ok=True)
    os.makedirs(f"{base_path}/data", exist_ok=True)

    # 1. Create Raw Logs with a "corruption" gap
    log_file = f"{base_path}/logs/raw/sensor_alpha_20231026.log"
    with open(log_file, "w") as f:
        for hour in range(0, 24):
            for minute in range(0, 60, 10):
                # Simulate humidity data
                humidity = round(random.uniform(40.0, 70.0), 2)
                f.write(f"TIMESTAMP: 2023-10-26 {hour:02d}:{minute:02d}:00 | SENSOR: Sensor_Node_Alpha | HUMIDITY: {humidity}%\n")

    # 2. Create a broken script
    broken_script = f"""
import os
import requests

def process_logs():
    # BUG: Wrong path and missing error handling
    log_path = "/wrong/path/to/logs" 
    with open(log_path, 'r') as f:
        data = f.readlines()
    
    # BUG: Incorrect parsing logic
    for line in data:
        val = line.split("|")[2].split(":")[1].replace("%", "").strip()
        # Missing logic to send data
        print(f"Processing {{val}}")

if __name__ == "__main__":
    process_logs()
"""
    with open(f"{base_path}/scripts/monitor_sync.py", "w") as f:
        f.write(broken_script)

    # 3. Initialize a mock state file for the "API" to record hits
    with open(f"{base_path}/api_state.json", "w") as f:
        json.dump({"received_reports": []}, f)

if __name__ == "__main__":
    setup_environment()
    print("Environment built successfully at assets/data_408")
