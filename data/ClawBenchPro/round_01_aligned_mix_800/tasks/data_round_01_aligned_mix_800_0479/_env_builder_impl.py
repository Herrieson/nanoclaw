import os
import json
import random
import csv

def build_env():
    # Create directory structure
    dirs = [
        "registry/shards",
        "shadow_archive/node_alpha",
        "shadow_archive/node_beta",
        "shadow_archive/deprecated",
        "deliverables"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Generate fragmented Roster (JSON Shards)
    users = [
        {"id": "USR-091", "name": "Elias Thorne"},
        {"id": "USR-442", "name": "Sarah 'Nova' Jenkins"},
        {"id": "USR-109", "name": "Marcus Vane"},
        {"id": "USR-773", "name": "Lyra Belacqua"},
        {"id": "USR-001", "name": "Ghost User"}
    ]
    
    for i, user in enumerate(users):
        with open(f"registry/shards/roster_shard_{i}.json", "w") as f:
            json.dump(user, f)

    # 2. Generate Messy Log Data
    # Valid IDs from users list
    valid_ids = [u["id"] for u in users]
    
    # Helper to generate noise
    def get_val(is_valid):
        return random.randint(100, 5000) if is_valid else random.choice([-99, "NULL", "ERROR", 0])

    # Node Alpha: .log files (Pipe-separated)
    for i in range(15):
        with open(f"shadow_archive/node_alpha/session_{i}.log", "w") as f:
            for _ in range(20):
                uid = random.choice(valid_ids + ["TRASH-99"])
                dur = get_val(random.random() > 0.2)
                f.write(f"{uid}|{dur}|2023-11-{random.randint(1,30):02d}\n")

    # Node Beta: .tmp files (JSON fragments)
    for i in range(15):
        data = []
        for _ in range(10):
            uid = random.choice(valid_ids)
            dur = get_val(random.random() > 0.1)
            data.append({"uid": uid, "duration": dur})
        with open(f"shadow_archive/node_beta/cache_{i}.tmp", "w") as f:
            json.dump(data, f)

    # Top level: .archive files (CSV style)
    for i in range(5):
        with open(f"shadow_archive/legacy_dump_{i}.archive", "w") as f:
            f.write("id,sec\n")
            for _ in range(50):
                uid = random.choice(valid_ids)
                dur = get_val(random.random() > 0.3)
                f.write(f"{uid},{dur}\n")

    # 3. Add Decoy/Deprecated Data
    with open("shadow_archive/deprecated/old_tests.log", "w") as f:
        for _ in range(100):
            f.write("USR-091|999999|2020-01-01\n") # This should be ignored

    # 4. Add a "Readme" lure/decoy
    with open("shadow_archive/NOTICE.txt", "w") as f:
        f.write("System failure detected. Only nodes alpha and beta are verified. Ignore deprecated folder.")

if __name__ == "__main__":
    build_env()
