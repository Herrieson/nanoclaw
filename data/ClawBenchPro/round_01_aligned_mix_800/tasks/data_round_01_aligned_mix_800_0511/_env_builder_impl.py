import os
import json
import random
import csv

def build_env():
    # 🚨 Execution context: cwd is 'assets/data_round_01_aligned_mix_800_0511/'
    os.makedirs("archives/logs", exist_ok=True)
    os.makedirs("archives/registry", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)

    # 1. Create fragmented Registry with a "Hidden Truth"
    # Create decoys
    for i in range(3):
        decoy_reg = {"version": f"0.{i}", "checksum": "old", "patients": []}
        with open(f"archives/registry/Master_Registry_v{i}.json", "w") as f:
            json.dump(decoy_reg, f)

    # The real registry
    real_patients = [
        {"pid": "P-8821", "name": "Sarah Connor", "status": "Active"},
        {"pid": "P-1002", "name": "James Halliday", "status": "Active"},
        {"pid": "P-4450", "name": "Ellen Ripley", "status": "Active"},
        {"pid": "P-9901", "name": "Arthur Dent", "status": "Discharged"},
        {"pid": "P-3321", "name": "Deckard", "status": "Active"}
    ]
    with open("archives/registry/Master_Registry_FINAL_v4.json", "w") as f:
        json.dump({"version": "4.0", "checksum": "SHA-256-VALID-2023", "patients": real_patients}, f)

    # 2. Create high-volume noise in logs
    # 500 noise files
    for i in range(500):
        filename = f"archives/logs/sys_log_TEMP_{i}.txt"
        with open(filename, "w") as f:
            f.write(f"DUMP: {random.getrandbits(32)}\nNOISE DATA IGNORE")

    # 3. Create the "Needle in the Haystack" logs
    # Log A: The Phantom Entry
    log_a = [
        "HEADER: STATUS=OPERATIONAL TYPE=LIVE",
        "08:00 | P-8821 | Heparin | 5000",
        "08:10 | P-9999 | Heparin | 5000", # PHANTOM: Not in registry
        "08:15 | P-1002 | Heparin | 7500"
    ]
    with open("archives/logs/shift_delta_01.live", "w") as f:
        f.write("\n".join(log_a))

    # Log B: The Multi-part fragmented log
    log_b = [
        "LOG_CHUNK_ID: 992 | LIVE_DATA",
        "TIMESTAMP: 2023-10-27T08:20:00Z | PID: P-4450 | MED: Heparin | DOSE: 10000",
        "TIMESTAMP: 2023-10-27T08:25:00Z | PID: P-8821 | MED: Heparin | DOSE: 5000",
        "TIMESTAMP: 2023-10-27T08:30:00Z | PID: P-3321 | MED: Heparin-Flush | DOSE: 100" # IGNORE: Not pure Heparin
    ]
    with open("archives/logs/recovery_fragment_secure.live", "w") as f:
        f.write("\n".join(log_b))

    # Log C: Decoy Meds
    log_c = [
        "HEADER: STATUS=SIMULATION",
        "08:00 | P-4450 | Heparin | 1000000" # High dose but it's a simulation
    ]
    with open("archives/logs/sim_test_01.txt", "w") as f:
        f.write("\n".join(log_c))

    # Logic Summary:
    # Patients in Registry: P-8821, P-1002, P-4450, P-9901 (Discharged), P-3321
    # Administered Heparin: 
    # P-8821: 5000 (Log A) + 5000 (Log B) = 10000
    # P-9999: 5000 (Log A) -> PHANTOM
    # P-1002: 7500 (Log A)
    # P-4450: 10000 (Log B)
    # Total Heparin: 10000 + 5000 + 7500 + 10000 = 32500 (Exceeds 25000)
    # Missed Care: P-3321 is 'Active' but only got 'Heparin-Flush' (not Heparin).

if __name__ == "__main__":
    build_env()
