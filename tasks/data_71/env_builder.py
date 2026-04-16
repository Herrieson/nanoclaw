import os
import json
import base64

def build_env():
    base_path = "assets/data_71"
    os.makedirs(os.path.join(base_path, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "scripts"), exist_ok=True)

    # 1. Generate Binary Log with Base64 Hidden Data
    # The real PID values: Kp=12.5, Ki=0.8, Kd=2.1
    calib_data = "Kp=12.5;Ki=0.8;Kd=2.1"
    encoded_data = base64.b64encode(calib_data.encode()).decode()
    
    binary_content = b"\x00\xFF\xDEAD\xBEEF" + b"Random Noise" * 10
    binary_content += b"CALIB_SIG:" + encoded_data.encode() + b":END_SIG"
    binary_content += b"\x00\x11\x22" * 5

    with open(os.path.join(base_path, "logs/telemetry_raw.bin"), "wb") as f:
        f.write(binary_content)

    # 2. Initial (Wrong) Controller Config
    config = {
        "target_force": 5000,
        "pid": {"Kp": 0, "Ki": 0, "Kd": 0},
        "material": "7075-T6"
    }
    with open(os.path.join(base_path, "controller_config.json"), "w") as f:
        json.dump(config, f, indent=4)

    # 3. Buggy Control Logic
    control_logic = """
import json
import math

def calculate_stress(force, area):
    # BUG: Multiplying instead of dividing, and missing safety factor
    # Reality: Stress = Force / Area. 
    return force * area 

def run_test():
    with open('../controller_config.json', 'r') as f:
        cfg = json.load(f)
    
    if cfg['pid']['Kp'] == 0:
        raise ValueError("PID parameters not calibrated!")

    # Area of the mount in mm^2
    area = 25.0
    force = cfg['target_force']
    
    stress = calculate_stress(force, area)
    
    # Safety limit 500 MPa
    if stress > 500:
        print(f"CRITICAL ERROR: Calculated stress {stress} MPa exceeds safety limit!")
        raise Exception("SafetyStopException")
    
    print(f"Test passed with stress: {stress} MPa")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(e)
"""
    with open(os.path.join(base_path, "scripts/control_logic.py"), "w") as f:
        f.write(control_logic.strip())

if __name__ == "__main__":
    build_env()
