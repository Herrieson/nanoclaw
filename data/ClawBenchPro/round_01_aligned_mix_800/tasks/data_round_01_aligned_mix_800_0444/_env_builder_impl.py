import os
import json
import random
import uuid

def build_env():
    # Setup base directories
    base_dirs = ["archive", "deliverables"]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Information Fragmentation: Split the catalog into pieces
    catalog_dir = "archive/system/config/assets"
    os.makedirs(catalog_dir, exist_ok=True)
    
    green_assets = {f"GRN-{i:03}": {"name": f"Green-Tech-Model-{i}", "category": "Green"} for i in range(1, 21)}
    std_assets = {f"STD-{i:03}": {"name": f"Standard-Tool-{i}", "category": "Standard"} for i in range(1, 81)}
    
    # Write catalog in fragments
    with open(f"{catalog_dir}/part_alpha.json", "w") as f:
        json.dump(dict(list(green_assets.items())[:10] + list(std_assets.items())[:40]), f)
    with open(f"{catalog_dir}/part_omega.json", "w") as f:
        json.dump(dict(list(green_assets.items())[10:] + list(std_assets.items())[40:]), f)

    # 2. Scale Simulation & Noise: Scattered Sales Logs
    reps = ["Carlos", "Sarah", "Elena", "Marcus"]
    all_assets = {**green_assets, **std_assets}
    asset_ids = list(all_assets.keys())
    
    # Create 50 messy folders, only some contain "valid" logs
    valid_contracts = []
    for i in range(50):
        folder_path = f"archive/logs/node_{i:02}"
        os.makedirs(folder_path, exist_ok=True)
        
        # Decide if this is a "real" log or junk
        is_valid = i % 3 == 0
        suffix = "final" if is_valid else "draft_temp"
        filename = f"sales_dump_{uuid.uuid4().hex[:6]}_{suffix}.log"
        
        num_entries = random.randint(10, 20)
        content = []
        if is_valid:
            content.append("TIMESTAMP|CONTRACT_ID|REP|ASSET_ID") # Specific header for valid logs
        else:
            content.append("TEMP_ID;CONTENT;USER") # Junk header
            
        for _ in range(num_entries):
            cid = f"CTX-{random.randint(1000, 9999)}"
            rep = random.choice(reps)
            aid = random.choice(asset_ids)
            if is_valid:
                content.append(f"2023-08-{random.randint(1,31):02}|{cid}|{rep}|{aid}")
                valid_contracts.append({"id": cid, "rep": rep, "aid": aid})
            else:
                content.append(f"DRAFT-{uuid.uuid4().hex[:4]};garbage;{rep}")
                
        with open(f"{folder_path}/{filename}", "w") as f:
            f.write("\n".join(content))

    # 3. Multi-hop Logic: Compliance forms hidden and missing
    compliance_dir = "archive/vault/legal/compliance/certificates"
    os.makedirs(compliance_dir, exist_ok=True)
    
    # Create decoy files
    for _ in range(100):
        with open(f"{compliance_dir}/TRASH-{random.randint(100,999)}_signed.txt", "w") as f:
            f.write("Void document.")

    # Only Green leases need forms. Let's make some missing.
    green_contract_ids = [c["id"] for c in valid_contracts if all_assets[c["aid"]]["category"] == "Green"]
    missing_count = 3
    missing_ids = random.sample(green_contract_ids, k=missing_count)
    
    for cid in green_contract_ids:
        if cid not in missing_ids:
            with open(f"{compliance_dir}/{cid}_signed.txt", "w") as f:
                f.write(f"Environmental Compliance Signed for {cid}")

    # 4. Decoy instructions: Add a "READ_ME_IMPORTANT.txt" with outdated info
    with open("archive/READ_ME_IMPORTANT.txt", "w") as f:
        f.write("All logs are in CSV format. Wait, actually we switched to pipes. Check the node folders.")

if __name__ == "__main__":
    build_env()
