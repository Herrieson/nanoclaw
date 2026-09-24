import os
import json
import random
import hashlib

def build_env():
    # Fix seed for strict deterministic reproducibility
    random.seed(42)

    # 1. Setup Directories
    dirs_to_create = [
        "sys_config",
        "sys_logs/stimuli",
        "raw_dumps/PORT_04",
        "raw_dumps/PORT_09",
        "raw_dumps/PORT_15",
        "raw_dumps/PORT_99",
        "analysis"
    ]
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)

    # 2. Generate Configuration Files (The Multi-hop Decoys)
    hardware_ini = """[CORTICAL_IMPLANT_MAPPINGS]
# Core EEG Channels
PORT_04=FZ
PORT_09=CZ
PORT_15=PZ

[PERIPHERAL_SENSORS]
# Ignore these for EEG artifact checks
PORT_99=ECG
PORT_12=TEMP
"""
    with open("sys_config/hardware.ini", "w") as f:
        f.write(hardware_ini)

    experiment_json = {
        "session_id": "CYBER-092-X",
        "stimulus_mapping": {
            "0x11": "N200",
            "0x42": "P300",
            "0x88": "SSVEP",
            "0xFF": "CALIBRATION_BLANK"
        },
        "sample_rate_hz": 100
    }
    with open("sys_config/experiment.json", "w") as f:
        json.dump(experiment_json, f, indent=4)

    # 3. Ground Truth Data Design (0 to 60000ms)
    # Target P300 Code: 0x42
    # EEG Ports: PORT_04 (FZ), PORT_09 (CZ), PORT_15 (PZ)
    
    # Event list: [(event_id, timestamp, is_clean, artifact_port, artifact_time, artifact_val, peak_time, peak_val)]
    p300_events = [
        ("EVT_001", 2000,  True,  None,      None,  None,    2250,  85.5),
        ("EVT_002", 5000,  False, "PORT_04", 5100,  1100.0,  5300,  60.0),  # Artifact in FZ
        ("EVT_003", 8000,  True,  None,      None,  None,    8320,  91.2),
        ("EVT_004", 11000, False, "PORT_09", 11400, -1250.0, 11350, 40.0),  # Artifact in CZ
        ("EVT_005", 15000, True,  None,      None,  None,    15380, 77.7),
        ("EVT_006", 18000, False, "PORT_15", 18150, 1500.5,  18300, 50.0),  # Artifact in PZ
        ("EVT_007", 22000, True,  None,      None,  None,    22220, 88.8),
        ("EVT_008", 26000, False, "PORT_04", 26490, -1050.0, 26200, 45.0),  # Artifact in FZ
        ("EVT_009", 30000, True,  None,      None,  None,    30300, 95.0),
        ("EVT_010", 34000, False, "PORT_09", 34010, 2000.0,  34350, 55.0),  # Artifact in CZ
        ("EVT_011", 38000, True,  None,      None,  None,    38280, 82.3),
        ("EVT_012", 42000, True,  None,      None,  None,    42350, 89.1),
        ("EVT_013", 46000, False, "PORT_15", 46450, 1001.0,  46300, 30.0),  # Artifact in PZ
        ("EVT_014", 50000, True,  None,      None,  None,    50200, 93.4),
        ("EVT_015", 54000, True,  None,      None,  None,    54390, 76.9),
    ]

    # Non-P300 decoy events
    decoy_events = [
        ("EVT_D01", 3500, "0x11"),
        ("EVT_D02", 6500, "0x88"),
        ("EVT_D03", 9500, "0x11"),
        ("EVT_D04", 13000, "0x88"),
        ("EVT_D05", 16500, "0xFF"),
        ("EVT_D06", 20000, "0x11"),
    ]

    # 4. Write Scattered Stimulus Event Files
    all_events = []
    for evt in p300_events:
        all_events.append({"id": evt[0], "t": evt[1], "code": "0x42"})
    for d_evt in decoy_events:
        all_events.append({"id": d_evt[0], "t": d_evt[1], "code": d_evt[2]})
    
    for evt_data in all_events:
        # Create a fragmented log with junk
        file_hash = hashlib.md5(evt_data['id'].encode()).hexdigest()[:8]
        filename = f"sys_logs/stimuli/log_mem_{file_hash}.txt"
        
        junk_header = f"KERNEL_INT: 0x{random.randint(1000, 9999)}\nMEM_DUMP: OK\n"
        payload = f"EVENT_ID:[{evt_data['id']}] STIM_CODE:[{evt_data['code']}] TIMESTAMP_MS:[{evt_data['t']}]\n"
        junk_footer = f"FLAGS: {random.choice(['DIRTY', 'CLEAN', 'SYNC'])}\n"
        
        with open(filename, "w") as f:
            f.write(junk_header + payload + junk_footer)
            
        # Also create pure garbage files to act as decoys
        if random.random() < 0.3:
            garbage_filename = f"sys_logs/stimuli/log_mem_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}.tmp"
            with open(garbage_filename, "w") as f:
                f.write("CORRUPTED SECTOR... READ ERROR 0xDEADBEEF\n")

    # 5. Build Time-Series Voltages Dictionary for Ports
    special_voltages = { "PORT_04": {}, "PORT_09": {}, "PORT_15": {}, "PORT_99": {} }
    
    for evt in p300_events:
        evt_id, t, is_clean, art_port, art_time, art_val, peak_time, peak_val = evt
        
        # Inject Artifact
        if not is_clean and art_port:
            special_voltages[art_port][art_time] = art_val
            
        # Inject CZ Peak (always inject a peak, but it only matters if trial is clean)
        special_voltages["PORT_09"][peak_time] = peak_val
        
        # Inject a decoy peak in ECG (PORT_99) to trick agents who don't filter ports
        special_voltages["PORT_99"][t + 300] = 2500.0  # Massive artifact, but shouldn't fail the trial

    # 6. Generate Data Stream Chunks
    ports = ["PORT_04", "PORT_09", "PORT_15", "PORT_99"]
    total_time = 60000
    chunk_size = 10000
    
    for port in ports:
        for chunk_start in range(0, total_time, chunk_size):
            chunk_end = chunk_start + chunk_size - 10
            filename = f"raw_dumps/{port}/mem_slice_{chunk_start:05d}_{chunk_end:05d}.dat"
            
            lines = []
            for t in range(chunk_start, chunk_start + chunk_size, 10):
                # 5% chance of system error line
                if random.random() < 0.05:
                    lines.append(f"SYS_WARN | BUFFER_LAG AT MEM 0x{random.randint(1000, 9999):X}")
                
                # Determine voltage
                if t in special_voltages[port]:
                    voltage = special_voltages[port][t]
                else:
                    # Background noise between -20 and 20
                    voltage = round(random.uniform(-20.0, 20.0), 2)
                    
                # Format: TRK: PORT_XX | T=002000 | VAL=0085.50uV | QOS=OK
                # Padded to mess with simple split() logic, forces regex or careful stripping
                padded_t = f"{t:06d}"
                padded_val = f"{voltage:08.2f}"
                
                line = f"TRK: {port} | T={padded_t} | VAL={padded_val}uV | QOS={random.choice(['OK', 'WARN', 'SYNC'])}"
                lines.append(line)
                
            with open(filename, "w") as f:
                f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    build_env()
