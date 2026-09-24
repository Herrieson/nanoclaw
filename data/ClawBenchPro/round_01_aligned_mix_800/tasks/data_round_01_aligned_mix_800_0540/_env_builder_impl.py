import os
import json
import random

def build_env():
    # Create the wasteland directory structure
    base_dir = "terminal_recovery"
    output_dir = "precinct_desk"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Sub-directories for fragmentation
    sub_dirs = ["radio_chatter/archived", "system_fragments/json_dumps", "legacy_backups/tmp_files"]
    for sd in sub_dirs:
        os.makedirs(os.path.join(base_dir, sd), exist_ok=True)

    # 1. Generate Noise (Decoys)
    for i in range(250):
        noise_path = os.path.join(base_dir, f"corrupt_seg_{i:04d}.log")
        with open(noise_path, "w") as f:
            f.write(f"SYSTEM_ERROR: Memory leak at {hex(random.getrandbits(32))}\nNo incident data found.")

    # 2. Generate Fragmented Real Data
    # Case 1: In a nested text file
    c1_path = os.path.join(base_dir, "radio_chatter/archived/dispatch_unit_88.txt")
    with open(c1_path, "w") as f:
        f.write("REC_START: 2023-10-14 02:00\nUNIT: 88\nMESSAGE: Arrived at scene. Residential burglary. CaseID: BLY-992. "
                "Stolen property: Designer handbag, appraised value: $4,500. Suspect: Male, 6ft, blurred neck tattoo. Fled in silver sedan.\nREC_END")

    # Case 2: In a JSON fragment
    c2_data = {
        "metadata": {"source": "mobile_unit", "timestamp": "2023-10-14T04:12:00Z"},
        "payload": {
            "case_id": "GTA-441",
            "status": "ACTIVE",
            "incident": "Vehicle Theft",
            "evidence": {
                "property_stolen": "Vintage Motorcycle",
                "estimated_value": 12500,
                "notes": "Suspect description: Caucasian male, skull tattoo on neck. Last seen at gas station."
            }
        }
    }
    with open(os.path.join(base_dir, "system_fragments/json_dumps/shard_A12.json"), "w") as f:
        json.dump(c2_data, f)

    # Case 3: Mixed in with backup files (Decoy backup vs real)
    for i in range(10):
        fname = f"case_snapshot_{i}.bak"
        path = os.path.join(base_dir, f"legacy_backups/tmp_files/{fname}")
        with open(path, "w") as f:
            if i == 7: # The "needle" in the haystack
                f.write("INTERNAL_REPORT\nID: LARC-771\nVAL: $850\nDESC: Suspect has a small rose tattoo on neck. Stolen: iPhone 15.")
            else:
                f.write("VOIDED_REPORT: Duplicate of 09-11 session. No data.")

    # Case 4: No tattoo, but high value
    c4_path = os.path.join(base_dir, "radio_chatter/archived/dispatch_unit_12.txt")
    with open(c4_path, "w") as f:
        f.write("CaseID: ROB-112. Status: OPEN. Value: $2,200. Suspect: Female, arm sleeve tattoo. No neck markings.")

    # Case 5: Deeply nested, different format
    os.makedirs(os.path.join(base_dir, "deep_scan/logs/2023/october"), exist_ok=True)
    with open(os.path.join(base_dir, "deep_scan/logs/2023/october/case_909.log"), "w") as f:
        f.write("REPORT_ID: UNK-909\nPROPERTY_LOSS: 300\nREMARKS: Suspect has 'Born to Lose' inked on neck. Foot pursuit failed.")

    # 3. Add more scale (irrelevant cases)
    for i in range(50):
        extra_path = os.path.join(base_dir, f"system_fragments/json_dumps/noise_{i}.json")
        with open(extra_path, "w") as f:
            json.dump({"case_id": f"X-{i}", "status": "CLOSED", "value": 0, "desc": "N/A"}, f)

if __name__ == "__main__":
    build_env()
