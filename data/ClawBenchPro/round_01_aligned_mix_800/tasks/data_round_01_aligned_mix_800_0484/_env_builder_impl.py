import os
import json
import random

def build_env():
    # Setup directories
    os.makedirs("archives/shards", exist_ok=True)
    os.makedirs("personnel/rosters", exist_ok=True)

    # 1. Fragmented Trail Data (Multi-format, scattered)
    trails = [
        ("Pine Ridge", 2, "Minor overgrowth"),
        ("Bear Creek", 5, "Massive fallen oak"),
        ("Summit Path", 4, "Dangerous washout"),
        ("Lake Loop", 1, "Clear"),
        ("Canyon Descent", 6, "Rockslide"),
        ("Meadow Trail", 3, "Muddy"),
        ("Deadmans Drop", 8, "Bridge collapsed"),
        ("Whispering Pines", 2, "Safe"),
        ("Gravel Pit", 5, "Unstable ground")
    ]

    for i, (name, level, status) in enumerate(trails):
        # Mix formats: some JSON, some TXT
        ext = "json" if i % 2 == 0 else "log"
        filename = f"archives/shards/shard_recovery_{i:03d}_{random.randint(1000, 9999)}.{ext}"
        if ext == "json":
            with open(filename, "w") as f:
                json.dump({"trail_id": f"TR-{i}", "name": name, "metrics": {"hazard": level}, "note": status}, f)
        else:
            with open(filename, "w") as f:
                f.write(f"ENTRY_ID: {i} | LOC: {name} | HAZARD_LVL: {level} | DESC: {status}\n")

    # Add 50 noise files to archives
    for i in range(50):
        with open(f"archives/shards/junk_temp_{i}.tmp", "w") as f:
            f.write("ERROR: Corrupted sector. Null data.")

    # 2. Scale & Noise in Personnel (Decoys & Metadata filtering)
    skills_pool = ["guiding", "first_aid", "clearing", "cooking", "hauling", "painting"]
    active_volunteers = [
        ("Samuel", ["clearing", "hauling"]),
        ("Marie", ["cooking", "clearing"]),
        ("Old_Ben", ["clearing"]),
        ("Sarah", ["first_aid", "clearing"])
    ]
    
    # Generate 200 decoy (inactive) volunteers
    for i in range(200):
        name = f"Volunteer_{i}"
        active_tag = "" # Inactive
        with open(f"personnel/rosters/record_{i:04d}.txt", "w") as f:
            f.write(f"Name: {name}\nStatus: INACTIVE\nSkills: {random.choice(skills_pool)}")

    # Generate the actual active volunteers with a specific naming pattern/content
    for name, skills in active_volunteers:
        # Clue: Filename contains [ACTIVE-2024]
        filename = f"personnel/rosters/record_[ACTIVE-2024]_{name}.txt"
        with open(filename, "w") as f:
            f.write(f"Name: {name}\nStatus: ACTIVE-2024\nSkills: {', '.join(skills)}")

    # Add a decoy "clearing" expert who is NOT active
    with open("personnel/rosters/record_999_DECOY.txt", "w") as f:
        f.write("Name: Traitor_Joe\nStatus: RETIRED\nSkills: clearing, explosives")

if __name__ == "__main__":
    build_env()
