import os
import json
import csv

def build_env():
    # CWD is already assets/data_round_01_aligned_mix_800_0395/
    os.makedirs("field_logs", exist_ok=True)
    
    # Generate some messy files
    
    # File 1: CSV containing SCADA data with waveform hashes instead of direct metrics
    csv_data = [
        ["node_id", "status", "waveform_hash", "active_power_mw"],
        ["NODE_A_WIND", "active", "HASH_A1B2", "10.5"], # Sag: 0.02, Freq: 0.05 -> Compliant
        ["NODE_B_SOLAR", "active", "HASH_C3D4", "5.0"], # Sag: 0.06, Freq: 0.02 -> Fail sag
        ["NODE_C_BESS", "inactive", "HASH_E5F6", "12.0"] # Fail status
    ]
    with open("field_logs/substation_alpha_telemetry.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # File 2: JSON containing Inverter logs with waveform hashes
    json_data = [
        {
            "node_id": "NODE_D_SOLAR",
            "status": "active",
            "telemetry": {
                "waveform_hash": "HASH_G7H8", # Sag: 0.04, Freq: 0.15 -> Fail freq
                "active_power_mw": 8.2
            }
        },
        {
            "node_id": "NODE_E_WIND",
            "status": "active",
            "telemetry": {
                "waveform_hash": "HASH_I9J0", # Sag: 0.01, Freq: 0.08 -> Compliant
                "active_power_mw": 14.3 
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
