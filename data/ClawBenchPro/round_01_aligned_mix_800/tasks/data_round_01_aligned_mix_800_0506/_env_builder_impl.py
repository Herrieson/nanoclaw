import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Root dirs
    os.makedirs("garden_data/eco_policies", exist_ok=True)
    
    # 1. Noise: Fake draft policies
    with open("garden_data/eco_policies/draft_rules_v1.txt", "w", encoding="utf-8") as f:
        f.write("Banned species draft: Heirloom Tomato, Sunflowers. Wait, nevermind, these are fine.")
    with open("garden_data/eco_policies/policy_meeting_notes.md", "w", encoding="utf-8") as f:
        f.write("- Discussed banning carrots.\n- Need to verify if Bamboo is an issue.")
        
    # 2. Clue: Official invasive list
    official_list = ["English Ivy", "Kudzu", "Japanese Knotweed", "Purple Loosestrife", "Bamboo", "Tree of Heaven"]
    with open("garden_data/eco_policies/official_invasive_species_2024.json", "w", encoding="utf-8") as f:
        json.dump(official_list, f, indent=4)

    # Base data for generation
    random.seed(42)
    names = [f"Neighbor_{i}" for i in range(1, 150)]
    plants = [
        "Milkweed", "Heirloom Tomato", "Sunflowers", "Carrot", "Basil", 
        "English Ivy", "Kudzu", "Japanese Knotweed", "Bamboo"
    ]
    zones = ["north", "south", "east", "west"]
    years = ["2022", "2023", "2024"]

    # 3. Mass generation & Fragmentation
    for year in years:
        for zone in zones:
            zone_path = f"garden_data/signups/{year}/zone_{zone}"
            os.makedirs(zone_path, exist_ok=True)
            
            # Generate random number of files per zone/year
            num_files = random.randint(30, 80)
            
            for _ in range(num_files):
                uid = f"req_{random.randint(100000, 999999)}"
                name = random.choice(names)
                plant = random.choice(plants)
                status = random.choice(["CONFIRMED", "CONFIRMED", "CONFIRMED", "CANCELLED", "PENDING"])
                
                # Introduce dirty data for hours
                hours_choice = random.choice([1, 2, 3, 5, 10, "two", "N/A", "", None, 4.5])
                if isinstance(hours_choice, float):
                    hours_choice = int(hours_choice) # keep it mostly int or string
                
                # Generate timestamp
                month = random.randint(1, 4)
                day = random.randint(1, 28)
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                ts = f"{year}-0{month}-{day:02d}T{hour:02d}:{minute:02d}:00Z"
                
                record = {
                    "submission_id": uid,
                    "name": name,
                    "requested_seed": plant,
                    "pledged_hours": hours_choice,
                    "status": status,
                    "timestamp": ts
                }
                
                with open(os.path.join(zone_path, f"{uid}.json"), "w", encoding="utf-8") as f:
                    json.dump(record, f, indent=2)

if __name__ == "__main__":
    build_env()
