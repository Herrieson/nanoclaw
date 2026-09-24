import os
import json
import random
import csv

def build_env():
    # Constants
    FORBIDDEN_FONTS = ["Papyrus", "Comic Sans"]
    FORBIDDEN_COLORS = ["#000000", "#FFFFFF"]
    VALID_FONTS = ["Helvetica", "Futura", "Roboto", "Inter", "Garamond"]
    VALID_COLORS = ["#FF0055", "#7700FF", "#00D4FF", "#39FF14", "#FFBD00"]
    ARTISTS = ["Leo Vance", "Mia Wallace", "Noah Trent", "Ava Smith", "Zoe Barnes", "Liam Gallagher", "Elena Rossi", "Marcus Thorne"]
    CONCEPTS = ["Cyber Sunset", "Jungle Vibe", "The Void", "Neon Nights", "Cloud Nine", "Electric Ocean", "Solar Flare", "Prism Gate"]
    
    # Create directory structure
    os.makedirs("raw_workspace/deep_storage/temp_v1", exist_ok=True)
    os.makedirs("raw_workspace/backups/old_assets", exist_ok=True)
    os.makedirs("mapping_protocols", exist_ok=True)
    os.makedirs("archive", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create a fragmented and noisy artist registry
    # Part 1: A messy CSV
    with open("mapping_protocols/registry_part_A.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Artist Name"])
        for i, name in enumerate(ARTISTS[:4]):
            writer.writerow([f"ID_{100+i}", name])
    
    # Part 2: A weird semi-structured text file
    with open("mapping_protocols/registry_part_B.txt", "w", encoding="utf-8") as f:
        f.write("--- INTERNAL USE ONLY ---\n")
        for i, name in enumerate(ARTISTS[4:]):
            f.write(f"REF_ID: {104+i} | NAME: {name}\n")

    # 2. Create the "Real" assets mixed with "Decoys"
    all_concept_data = []
    for i in range(len(CONCEPTS)):
        # Half of the data is "bad" based on Fiona's rules
        is_bad = i % 2 == 0
        font = random.choice(FORBIDDEN_FONTS) if is_bad else random.choice(VALID_FONTS)
        color = random.choice(FORBIDDEN_COLORS) if is_bad else random.choice(VALID_COLORS)
        
        concept_info = {
            "id": f"ID_{100+i}",
            "title": CONCEPTS[i],
            "metadata": {
                "typography": font,
                "branding": {"palette": [color, "#121212"]}
            }
        }
        all_concept_data.append(concept_info)

    # Distribute real files in deep folders with inconsistent extensions
    for i, data in enumerate(all_concept_data):
        ext = ".manifest" if i % 2 == 0 else ".meta"
        path = "raw_workspace/deep_storage/temp_v1" if i < 4 else "raw_workspace/backups/old_assets"
        filename = f"concept_hash_{random.getrandbits(32)}{ext}"
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            json.dump(data, f)

    # 3. Scale Simulation: Generate 200+ Decoy files
    for i in range(250):
        path = random.choice(["raw_workspace/deep_storage/temp_v1", "raw_workspace/backups/old_assets"])
        decoy_ext = random.choice([".log", ".tmp", ".manifest", ".meta", ".bak"])
        filename = f"trash_{i}{decoy_ext}"
        
        # Some decoys look like JSON but are empty or irrelevant
        content = random.choice([
            "DEBUG: System heartbeat ok",
            "TODO: Buy milk",
            json.dumps({"error": "corrupted profile"}),
            "Wait, why am I here?"
        ])
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
