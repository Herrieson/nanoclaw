import os
import json
import random
import csv

def build_env():
    # 🚨 Executed in assets/data_round_01_aligned_mix_800_0438/
    os.makedirs("raw_archives/sector_alpha/logs", exist_ok=True)
    os.makedirs("raw_archives/sector_beta/temp", exist_ok=True)
    os.makedirs("recipes_logic", exist_ok=True)
    os.makedirs("pantry_audit", exist_ok=True)

    # 1. The Key: Manifest Schema (Hidden in a nested directory)
    schema = {
        "valid_prefixes": ["TXN_REAL_", "REC_V2_"],
        "target_categories": ["Protein", "Produce", "Grains"],
        "status_flag": "AUTHORIZED"
    }
    with open("raw_archives/manifest_schema_v2.json", "w") as f:
        json.dump(schema, f)

    # 2. Generate Scale: 500+ files with noise
    categories = ["Protein", "Produce", "Grains", "Industrial", "Waste", "Medical"]
    items_map = {
        "Protein": ["Chicken Breast", "Beef Roast", "Dried Soy", "Canned Tuna"],
        "Produce": ["Apples", "Potatoes", "Carrots", "Onions", "Cabbage"],
        "Grains": ["Flour", "Rice", "Yeast", "Barley"]
    }

    # Generate noise files
    for i in range(200):
        fname = f"raw_archives/sector_alpha/logs/log_fragment_{i:03d}.txt"
        with open(fname, "w") as f:
            f.write(f"PING... {random.random()} ... STATUS: IDLE\n")

    # Generate fragmented receipt data
    # Real data mixed with decoys
    real_data_pool = []
    
    # Target values to ensure consistency
    # Store A (CSV style in fragments)
    for i in range(50):
        is_real = random.choice([True, False])
        prefix = "TXN_REAL_" if is_real else "TXN_VOID_"
        filename = f"raw_archives/sector_alpha/logs/{prefix}{i:03d}.csv"
        
        cat = random.choice(categories)
        item = random.choice(items_map.get(cat, ["Useless Junk"]))
        price = round(random.uniform(5.0, 50.0), 2)
        qty = random.randint(1, 5)
        
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["meta_id", "item_name", "category", "cost", "quantity", "status"])
            writer.writerow([f"ID-{i}", item, cat, str(price), str(qty), "AUTHORIZED" if is_real else "PENDING"])
            if is_real and cat in schema["target_categories"]:
                real_data_pool.append({"item": item, "cat": cat, "cost": price, "qty": qty})

    # Store B (JSON fragments in Beta sector)
    for i in range(50):
        is_real = random.choice([True, False, False]) # Rare real data
        prefix = "REC_V2_" if is_real else "DUMP_V1_"
        filename = f"raw_archives/sector_beta/temp/{prefix}{i:03d}.json"
        
        cat = random.choice(categories)
        item = random.choice(items_map.get(cat, ["Rust Scrap"]))
        data = {
            "entry": {
                "label": item,
                "group": cat,
                "pricing": {"amt": round(random.uniform(2.0, 30.0), 2), "unit": "USD"},
                "count": random.randint(1, 3),
                "auth_code": "AUTHORIZED" if is_real else "REJECTED"
            }
        }
        with open(filename, "w") as f:
            json.dump(data, f)
        
        if is_real and cat in schema["target_categories"]:
            real_data_pool.append({"item": item, "cat": cat, "cost": data["entry"]["pricing"]["amt"], "qty": data["entry"]["count"]})

    # 3. Recipes (The Logic Requirement)
    # The agent needs to find these items in the real_data_pool
    recipes = {
        "Stewardship Stew": ["Beef Roast", "Potatoes", "Carrots", "Onions", "Beef Stock"],
        "Emergency Hardtack": ["Flour", "Salt", "Water"]
    }
    with open("recipes_logic/active_requirements.json", "w") as f:
        json.dump(recipes, f)

    # Note: "Beef Stock", "Salt", "Water" are not in the generated items pool, so they will be missing.
    # Onions and Potatoes might be missing depending on the random seed, but most likely some will be there.

if __name__ == "__main__":
    build_env()
