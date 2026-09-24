import os
import json
import csv
import random

def build_env():
    # Setup directory structure
    base_dirs = [
        "archive/manifest_shards",
        "archive/geo_fragments",
        "logs/system",
        "logs/legacy_trash",
        "archive/backup_v1"
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Create fragmented Manifest
    passengers = [
        ("T-UX001", "Arthur Morgan"), ("T-UX002", "John Marston"),
        ("T-UX003", "Sadie Adler"), ("T-UX004", "Charles Smith"),
        ("T-UX005", "Bill Williamson"), ("T-UX006", "Dutch van der Linde"),
        ("T-UX007", "Hosea Matthews"), ("T-UX008", "Lenny Summers"),
        ("T-UX009", "Abigail Roberts"), ("T-UX010", "Jack Marston")
    ]
    
    # Split manifest into 5 shards with noise
    for i in range(5):
        shard_file = f"archive/manifest_shards/manifest_part_{i+1}.csv"
        subset = passengers[i*2 : (i+1)*2]
        with open(shard_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ticket_id", "full_name", "status"])
            for p in subset:
                writer.writerow([p[0], p[1], "Confirmed"])
        # Add a noise file
        with open(f"archive/manifest_shards/shard_{i+1}_temp.tmp", "w") as f:
            f.write("TEMP_DATA_IGNORE")

    # 2. Create high-noise Waiver Logs
    # Only these passengers signed: 1, 2, 4, 5, 7, 8, 10 (Missing: 3, 6, 9)
    signed_ids = ["T-UX001", "T-UX002", "T-UX004", "T-UX005", "T-UX007", "T-UX008", "T-UX010"]
    
    for i in range(100):
        log_name = f"logs/system/daily_log_{i:03d}.txt"
        if i % 10 == 0 and signed_ids:
            # Valid log
            log_name = f"logs/system/sig_v4_event_{i:03d}.txt"
            ticket = signed_ids.pop(0)
            content = f"TIMESTAMP: 2023-10-12T10:00:00Z | EVENT: SIG_CAPTURE | ID: {ticket} | STATUS: OK"
        else:
            # Noise log
            content = f"SYSTEM_IDLE... Random Entropy: {random.random()}"
        
        with open(log_name, "w") as f:
            f.write(content)

    # 3. Create Geo Fragments with swapped coordinates
    # Ohio: Lat ~40, Lon ~-82. We store them as Lat: -82, Lon: 40 (Swapped)
    landmarks = [
        {"seq": 1, "name": "Ancient Burial Mound", "y": -82.32, "x": 39.96},
        {"seq": 2, "name": "Conkle's Hollow", "y": -82.57, "x": 39.45},
        {"seq": 3, "name": "Serpent Mound", "y": -83.43, "x": 39.02},
        {"seq": 4, "name": "Hopewell Furnace", "y": -82.98, "x": 40.01}
    ]
    
    for i, lm in enumerate(landmarks):
        fname = f"archive/geo_fragments/loc_{random.randint(1000,9999)}_data.json"
        # The prompt says lat and lon are swapped. 
        # In this malformed JSON, 'lat' will hold the negative longitude value.
        data = {
            "sequence_id": lm["seq"],
            "point_name": lm["name"],
            "lat": lm["y"], # WRONG: This is actually the Longitude
            "lon": lm["x"]  # WRONG: This is actually the Latitude
        }
        with open(fname, "w") as f:
            json.dump(data, f)
            
    # Add decoy landmarks in a deprecated folder
    os.makedirs("archive/geo_fragments/_deprecated", exist_ok=True)
    with open("archive/geo_fragments/_deprecated/old_route.json", "w") as f:
        json.dump({"note": "ignore this", "lat": 0, "lon": 0}, f)

if __name__ == "__main__":
    build_env()
