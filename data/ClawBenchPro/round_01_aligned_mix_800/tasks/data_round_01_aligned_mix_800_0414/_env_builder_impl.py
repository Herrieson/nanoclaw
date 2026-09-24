import os
import json
import random
import uuid

def build_env():
    # 🚨 Current working directory is assets/data_round_01_aligned_mix_800_0414/
    base_dir = "store_data"
    os.makedirs(f"{base_dir}/system_configs", exist_ok=True)
    os.makedirs(f"{base_dir}/logs/raw_shards", exist_ok=True)
    os.makedirs(f"{base_dir}/hr_obfuscated", exist_ok=True)

    # 1. Product Mapping (Multi-hop clue)
    product_map = {
        "Global Heritage": ["GH-ALPHA", "PRJ-HERITAGE", "Global_Heritage_V2", "GH_COLLECTION"],
        "Common Goods": ["CG-BASIC", "HOUSEHOLD-STUFF"]
    }
    with open(f"{base_dir}/system_configs/internal_codes.json", 'w') as f:
        json.dump({"project_naming_conventions": product_map}, f)

    # 2. Manager Data (Fragmented and Obfuscated)
    managers = [
        {"id": "UID-9901", "first": "Marcus", "last": "Vance"},
        {"id": "UID-2210", "first": "Sarah", "last": "Jenkins"},
        {"id": "UID-4453", "first": "David", "last": "Kim"},
        {"id": "UID-7762", "first": "Chloe", "last": "Adams"}
    ]
    # Split HR data into two files to force a join
    names_shards = [{"uuid": m["id"], "full_name": f"{m['first']} {m['last']}"} for m in managers]
    with open(f"{base_dir}/hr_obfuscated/employee_roster_part_a.json", "w") as f:
        json.dump(names_shards[:2], f)
    with open(f"{base_dir}/hr_obfuscated/employee_roster_part_b.json", "w") as f:
        json.dump(names_shards[2:], f)

    # 3. Generating the "Waste" - 500 noise files
    for i in range(500):
        fname = f"log_shard_{uuid.uuid4().hex[:8]}.txt"
        with open(f"{base_dir}/logs/raw_shards/{fname}", "w") as f:
            f.write(f"SYSTEM_CHECK: Sensor {i} operational. Temp: {random.randint(20, 30)}C. No issues detected.")

    # 4. Generating the "Truth" - 5 Hidden valid cases + decoys
    target_products = product_map["Global Heritage"]
    valid_cases = [
        {"pid": "GH-ALPHA", "mid": "UID-9901", "msg": "Fake plastic garbage. No refund given.", "status": "Closed", "ref": "0.00"},
        {"pid": "PRJ-HERITAGE", "mid": "UID-2210", "msg": "Broken ceramic upon arrival. Manager refused to help.", "status": "Closed", "ref": "0"},
        {"pid": "GH_COLLECTION", "mid": "UID-4453", "msg": "The 'authentic' rug is synthetic. Absolute scam.", "status": "Closed", "ref": "0.0"},
        {"pid": "GH-ALPHA", "mid": "UID-7762", "msg": "Never received the item, but ticket marked closed with no refund.", "status": "Closed", "ref": "0.000"},
        {"pid": "Global_Heritage_V2", "mid": "UID-9901", "msg": "The carving was hollow wood, not solid. Terrible.", "status": "Closed", "ref": "0"}
    ]
    
    # Decoys (wrong product, or refund given, or open)
    decoys = [
        {"pid": "CG-BASIC", "mid": "UID-9901", "msg": "T-shirt size wrong.", "status": "Closed", "ref": "0.00"},
        {"pid": "GH-ALPHA", "mid": "UID-2210", "msg": "Box dented.", "status": "Closed", "ref": "15.00"},
        {"pid": "GH-ALPHA", "mid": "UID-4453", "msg": "Still waiting...", "status": "Open", "ref": "0.00"},
    ]

    all_data = valid_cases + decoys
    for idx, entry in enumerate(all_data):
        # Hidden in specialized JSON shards
        fname = f"critical_data_shard_{idx}_{uuid.uuid4().hex[:5]}.json"
        with open(f"{base_dir}/logs/raw_shards/{fname}", "w") as f:
            # Add some internal noise metadata
            json.dump({
                "meta": {"timestamp": "2023-10-12T10:00:00Z", "node": "NODE-04"},
                "payload": {
                    "ticket_info": {
                        "identifier": f"TKT-{random.randint(1000, 9999)}",
                        "product_code": entry["pid"],
                        "status_code": entry["status"],
                        "accounting": {"refunded_amt": entry["ref"]}
                    },
                    "content": entry["msg"],
                    "assignment": {"manager_uuid": entry["mid"]}
                }
            }, f)

if __name__ == "__main__":
    build_env()
