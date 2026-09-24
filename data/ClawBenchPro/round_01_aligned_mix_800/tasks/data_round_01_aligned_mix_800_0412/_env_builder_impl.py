import os
import csv
import json
import random

def build_env():
    # Create the wasteland directory structure
    os.makedirs("archive/terminal_logs/recovery_01/sub_alpha", exist_ok=True)
    os.makedirs("archive/terminal_logs/recovery_02/temp_cache", exist_ok=True)
    os.makedirs("archive/terminal_logs/nodes/node_88", exist_ok=True)
    os.makedirs("feed_fragments/invoices/legacy", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. Fragmented & Noisy Logs
    # Correct Month: October 2023
    log_templates = [
        "TIMESTAMP: 2023-10-12\nLog Entry: {id} shows signs of {symptom}. Need vet.",
        "TIMESTAMP: 2022-05-10\nOLD DATA: {id} had {symptom} last year. Ignore.", # Noise (wrong year)
        "RECOVERY_FRAGMENT: 2023-10-15\n{id} status: {symptom}. High priority.",
        "SYSTEM_CHECK: 2023-10-20\nAll clear except {id} which is {symptom}."
    ]
    
    animals_at_risk = [("Cow-402", "fever"), ("Horse-X9", "limping"), ("Sheep-112", "fever"), ("Pig-05", "limping")]
    
    # Generate hundreds of noise files
    for i in range(150):
        path = f"archive/terminal_logs/recovery_{random.randint(1,2)}/node_{i}.log"
        if not os.path.exists(os.path.dirname(path)): os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w") as f:
            if i < 4: # Insert real clues
                f.write(log_templates[0].format(id=animals_at_risk[i][0], symptom=animals_at_risk[i][1]))
            else:
                f.write(f"TIMESTAMP: 2023-09-{random.randint(1,30)}\nNothing to report for {random.randint(100,999)}.")

    # 2. Multi-format & Scale Feed Data
    # CSV Fragment
    with open("feed_fragments/oct_batch_1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "material", "weight_lbs", "notes"])
        writer.writerow(["2023-10-01", "Alfalfa", "1250.5", "Prime cut"])
        writer.writerow(["2023-10-02", "Corn", "800", "Dry"])

    # JSON Fragment
    json_data = [
        {"timestamp": "2023-10-05", "type": "Alfalfa", "mass": 949.5, "unit": "lbs"},
        {"timestamp": "2023-10-06", "type": "Oats", "mass": 200, "unit": "lbs"}
    ]
    with open("feed_fragments/invoices/recovery_json.txt", "w") as f: # Deceptive extension
        json.dump(json_data, f)

    # Raw Text Fragment (Multi-hop logic: requires parsing unstructured text)
    with open("feed_fragments/invoices/legacy/notes_oct.txt", "w") as f:
        f.write("Memo: Received shipment of Alfalfa on Oct 10th. Total was 800 lbs. Half was moldy but we kept all 800.\n")
        f.write("Memo: Corn shipment 500 lbs.")

    # 3. Decoys
    with open("feed_fragments/invoices/legacy/old_alfalfa_dont_count.csv", "w") as f:
        f.write("Date,Item,Weight\n2022-10-10,Alfalfa,5000") # Wrong year decoy

if __name__ == "__main__":
    build_env()
