import os
import json
import random
import uuid

def build_env():
    # CWD is assets/data_round_01_aligned_mix_800_0595/
    base_dir = "field_logs"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create a fragmented Registry (Metadata)
    # This maps Node IDs to their Status and Environment (PROD vs TEST)
    registry_dir = os.path.join(base_dir, "registry_fragments")
    os.makedirs(registry_dir, exist_ok=True)
    
    all_node_configs = []
    # Generate 50 nodes, but only some are PROD and Active
    for i in range(50):
        node_id = f"NODE_{1000 + i:X}"
        is_prod = random.choice([True, False])
        status = random.choice(["active", "inactive", "maintenance"])
        all_node_configs.append({"id": node_id, "env": "PROD" if is_prod else "TEST", "status": status})
        
    # Split registry into multiple messy JSON/txt files
    for i in range(0, 50, 10):
        chunk = all_node_configs[i:i+10]
        with open(os.path.join(registry_dir, f"reg_chunk_{uuid.uuid4().hex[:6]}.json"), "w") as f:
            json.dump(chunk, f)

    # 2. Create Telemetry Shards (The "Deep Nesting" and "Noise")
    # We will hide the real data among 500+ files
    shards_root = os.path.join(base_dir, "telemetry_shards")
    os.makedirs(shards_root, exist_ok=True)
    
    valid_nodes = [n["id"] for n in all_node_configs if n["env"] == "PROD" and n["status"] == "active"]
    
    # Generate fake folders to simulate scale
    for folder in ["legacy", "test_bench", "overflow", "temp_cache"]:
        os.makedirs(os.path.join(shards_root, folder), exist_ok=True)
        for _ in range(50):
            with open(os.path.join(shards_root, folder, f"err_{uuid.uuid4().hex}.log"), "w") as f:
                f.write("ERROR: INVALID_HANDSHAKE_AT_" + str(random.random()))

    # Generate the actual telemetry data mixed with noise
    # We'll put them in nested date-like structures
    for i, node_id in enumerate([n["id"] for n in all_node_configs]):
        # Deterministic but messy path
        sub_dir = os.path.join(shards_root, f"cycle_{i % 5}")
        os.makedirs(sub_dir, exist_ok=True)
        
        # Determine compliance
        # Pass: sag < 0.05 AND freq <= 0.1
        is_compliant = (i % 3 == 0) 
        if is_compliant:
            sag = random.uniform(0.001, 0.049)
            freq = random.uniform(0.01, 0.09)
            power = random.uniform(10.0, 50.0)
        else:
            # Randomly fail one or both
            sag = random.uniform(0.051, 0.1) if random.random() > 0.5 else 0.02
            freq = random.uniform(0.11, 0.2) if sag <= 0.05 else 0.05
            power = random.uniform(5.0, 10.0)

        data_format = random.choice(["json", "csv_fragment"])
        file_path = os.path.join(sub_dir, f"telemetry_{node_id}_{uuid.uuid4().hex[:4]}")
        
        if data_format == "json":
            with open(file_path + ".json", "w") as f:
                json.dump({"n_id": node_id, "metrics": {"v_sag": sag, "f_dev": freq, "p_mw": power}}, f)
        else:
            with open(file_path + ".txt", "w") as f:
                # Semi-structured text format
                f.write(f"HDR|{node_id}|TELEMETRY\nVAL|SAG:{sag}|FREQ:{freq}|PWR:{power}\nFOOTER|END")

    # 3. Add a "Red Herring" file in the root
    with open(os.path.join(base_dir, "FINAL_URGENT_README.txt"), "w") as f:
        f.write("Disregard all CSVs in the root. They are from the 2022 audit. - Jim")

if __name__ == "__main__":
    build_env()
