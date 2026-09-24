import os
import json
import csv

def build_env():
    # CWD is already assets/data_round_01_aligned_mix_800_0795/
    os.makedirs("field_logs", exist_ok=True)
    
    # Generate some messy files
    
    # File 1: CSV containing SCADA data
    csv_data = [
        ["node_id", "status", "voltage_sag_pu", "freq_dev_hz", "active_power_mw"],
        ["NODE_A_WIND", "active", "0.02", "0.05", "10.5"], # Compliant
        ["NODE_B_SOLAR", "active", "0.06", "0.02", "5.0"], # Fail sag (>= 0.05)
        ["NODE_C_BESS", "inactive", "0.01", "0.01", "12.0"] # Fail status
    ]
    with open("field_logs/substation_alpha_telemetry.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # File 2: JSON containing Inverter logs
    json_data = [
        {
            "node_id": "NODE_D_SOLAR",
            "status": "active",
            "telemetry": {
                "voltage_sag_pu": 0.04,
                "freq_dev_hz": 0.15, # Fail freq (> 0.1)
                "active_power_mw": 8.2
            }
        },
        {
            "node_id": "NODE_E_WIND",
            "status": "active",
            "telemetry": {
                "voltage_sag_pu": 0.01,
                "freq_dev_hz": 0.08,
                "active_power_mw": 14.3 # Compliant
            }
        }
    ]
    with open("field_logs/inverter_beta_logs.json", "w") as f:
        json.dump(json_data, f, indent=2)
        
    # File 3: Irrelevant noise due to low conscientiousness
    with open("field_logs/jimmy_soccer_schedule.txt", "w") as f:
        f.write("Saturday 9AM - Field 4\nSunday 11AM - Away game\nDon't forget the orange slices.")

if __name__ == "__main__":
    build_env()
