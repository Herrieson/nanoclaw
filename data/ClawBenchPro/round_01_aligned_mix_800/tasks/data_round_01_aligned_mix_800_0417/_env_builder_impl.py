import os
import json
import csv
import random

def build_env():
    # 1. Create a chaotic nested structure for inventory
    archives_dir = "archives"
    os.makedirs(archives_dir, exist_ok=True)
    
    # Sub-directories representing different "hubs"
    hubs = ["north_hub", "south_depot", "west_yard", "legacy_storage"]
    for hub in hubs:
        hub_path = os.path.join(archives_dir, hub)
        os.makedirs(hub_path, exist_ok=True)
        
        # Generate noise files
        for i in range(5):
            with open(os.path.join(hub_path, f"backup_{i}.bak"), "w") as f:
                f.write("STATUS: EXPIRED\npart_name,qty\nfake_part,100")
            with open(os.path.join(hub_path, f"temp_{i}.tmp"), "w") as f:
                f.write("junk data 0xCCFF")

    # The REAL data scattered in specific places
    # Real File 1: CSV in South Depot
    with open(os.path.join(archives_dir, "south_depot", "inv_manifest_v2.csv"), "w") as f:
        f.write("## METADATA ##\n## STATUS: ACTIVE ##\n")
        f.write("part_id,part_name,stock_level\n")
        f.write("P001,chrome_rims,15\n")
        f.write("P002,chassis_rail,0\n")  # Missing
        f.write("P003,diesel_tank,-1\n") # Missing
    
    # Real File 2: JSON in North Hub
    json_data = {
        "metadata": {"status": "ACTIVE", "version": "2024.1"},
        "entries": [
            {"name": "cab_shell", "stock": 5},
            {"name": "front_grille", "stock": "OUT"}, # Missing
            {"name": "led_headlights", "stock": "void"} # Missing
        ]
    }
    with open(os.path.join(archives_dir, "north_hub", "current_stock.json"), "w") as f:
        json.dump(json_data, f)

    # Real File 3: TXT fragments in West Yard
    with open(os.path.join(archives_dir, "west_yard", "notes.txt"), "w") as f:
        f.write("STATUS: ACTIVE\n")
        f.write("LOG: Received steering_column (qty: 2)\n")
        f.write("LOG: Received mud_flaps (qty: 0)\n") # Missing

    # 2. Create the Blueprint Maze
    specs_dir = "blueprints"
    os.makedirs(specs_dir, exist_ok=True)
    
    # Generate 50 noise files
    for i in range(50):
        with open(os.path.join(specs_dir, f"cad_log_{i:03d}.log"), "w") as f:
            f.write(f"Seed: {random.random()}\nNo measurement found.")

    # Hide the real spec in a slightly different filename
    with open(os.path.join(specs_dir, "final_blueprint_specs.txt"), "w") as f:
        f.write("--- Peterbilt 379 Official Scale Dimensions ---\n")
        f.write("Interior Dashboard: 2.5 inch\n")
        f.write("Sleeper Cab Extension: 25.4 cm\n") # 10.0 inch
        f.write("Main Frame Rail: 63.5 cm\n")      # 25.0 inch
        f.write("Bumper Width: 8.0 inch\n")
        f.write("Sun Visor: 4.5 cm\n")              # ~1.77 inch

    # Add a decoy blueprint with 'OLD' status
    with open(os.path.join(specs_dir, "old_blueprint.txt"), "w") as f:
        f.write("--- OLD SPECS ---\n")
        f.write("Main Frame Rail: 1000.0 inch\n") # Decoy value

if __name__ == "__main__":
    build_env()
