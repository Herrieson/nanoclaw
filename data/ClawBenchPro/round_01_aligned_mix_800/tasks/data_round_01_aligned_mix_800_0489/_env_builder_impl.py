import os
import json
import random
import uuid

def build_env():
    # Workspace root
    base = "workspace"
    os.makedirs(base, exist_ok=True)
    
    # --- 1. Fragmented RSVP Data (The Hunt) ---
    # We need 32 "Regular" eaters total.
    # Total entities generated: 500+ across multiple formats
    sub_dirs = ["archives", "tmp/scans", "backups/v2", "emails/drafts"]
    for d in sub_dirs:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    # Truth: 32 Regular, 8 Vegan, 10 Gluten-Free
    # Distribute them in messy files
    rsvps = []
    for _ in range(32): rsvps.append({"name": str(uuid.uuid4())[:8], "needs": "None", "valid": True})
    for _ in range(8): rsvps.append({"name": str(uuid.uuid4())[:8], "needs": "Vegan", "valid": True})
    for _ in range(10): rsvps.append({"name": str(uuid.uuid4())[:8], "needs": "Gluten-Free", "valid": True})
    
    # Add 400 "Noise" entries (invalid or old versions)
    for _ in range(400):
        rsvps.append({"name": "DELETED_" + str(uuid.uuid4())[:4], "needs": "None", "valid": False})

    random.shuffle(rsvps)

    # Chunk 1: CSV with noise
    with open(os.path.join(base, "archives/rsvp_dump.csv"), "w") as f:
        f.write("id,guest_name,restriction,status\n")
        for i, r in enumerate(rsvps[:150]):
            status = "VERIFIED" if r['valid'] else "OUTDATED"
            f.write(f"{i},{r['name']},{r['needs']},{status}\n")

    # Chunk 2: JSON fragments
    with open(os.path.join(base, "emails/drafts/parsed_rsvps.json"), "w") as f:
        json.dump([{"info": r} for r in rsvps[150:300] if r['valid']], f)

    # Chunk 3: Raw text log
    with open(os.path.join(base, "tmp/scans/manual_log.txt"), "w") as f:
        for r in rsvps[300:]:
            if r['valid']:
                f.write(f"ENTRY: {r['name']} | DIET: {r['needs']} | VERIFIED\n")
            else:
                f.write(f"TRASH: {r['name']} | IGNORE\n")

    # --- 2. The Recipe (Hidden & Multi-hop) ---
    # Recipe for 4 people: 12 tortillas, 2.0 lbs chicken, 16.0 oz cheese, 1.0 can sauce
    # But there's a "tweak" note.
    os.makedirs(os.path.join(base, "family_secrets"), exist_ok=True)
    with open(os.path.join(base, "family_secrets/grandma_base.json"), "w") as f:
        json.dump({
            "serves": 4,
            "ingredients": {
                "tortillas": 10, # Fake value
                "chicken_lbs": 2.0,
                "cheese_oz": 16.0,
                "sauce_cans": 1.0
            }
        }, f)
    
    with open(os.path.join(base, "family_secrets/corrections.txt"), "w") as f:
        f.write("NOTE: Grandma's base recipe is wrong about tortillas. Use 12 tortillas for 4 people, not 10.\n")
        f.write("Everything else in the JSON is correct for a 4-person batch.\n")

    # --- 3. Inventory (Scale Suppression) ---
    # Goal: Count ingredients for 32 people (Multiplier = 32/4 = 8)
    # Required: 96 tortillas, 16 lbs chicken, 128 oz cheese, 8 cans sauce
    pantry_path = os.path.join(base, "inventory")
    os.makedirs(pantry_path, exist_ok=True)
    
    # Scatter 100+ small inventory files, only files with "final" in name are accurate
    for i in range(50):
        with open(os.path.join(pantry_path, f"stock_check_{i}.log"), "w") as f:
            f.write(f"tortillas: {random.randint(1, 100)}\n")
    
    # The real stock
    stock = {
        "tortillas": 26,
        "chicken_lbs": 4.5,
        "cheese_oz": 28.0,
        "sauce_cans": 3.0
    }
    with open(os.path.join(pantry_path, "inventory_final_verified.json"), "w") as f:
        json.dump(stock, f)

if __name__ == "__main__":
    build_env()
