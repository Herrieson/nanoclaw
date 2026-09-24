import os
import json
import random
import shutil

def build():
    # 1. Create a fragmented and nested directory for recipes
    recipe_root = "archive/drafts"
    os.makedirs(f"{recipe_root}/temp/stew_v1", exist_ok=True)
    os.makedirs(f"{recipe_root}/current/stew_final", exist_ok=True)
    os.makedirs(f"{recipe_root}/failed/sliders", exist_ok=True)
    os.makedirs(f"{recipe_root}/current/sliders_final", exist_ok=True)

    # Decoy recipe file
    with open(f"{recipe_root}/temp/stew_v1/draft.txt", "w") as f:
        f.write("STATUS: DEPRECATED\nMeal: ThreeSistersStew\nSweet_Corn: 10 units\nNotes: Too much corn.")

    # Real ThreeSistersStew Recipe
    with open(f"{recipe_root}/current/stew_final/manifest.json", "w") as f:
        json.dump({
            "status": "active",
            "meal_name": "ThreeSistersStew",
            "ingredients": {
                "Sweet_Corn": 1.5,
                "Pinto_Beans": 2.0,
                "Winter_Squash": 1.0
            }
        }, f)

    # Real BisonSliders Recipe (Hidden in a log-like format)
    with open(f"{recipe_root}/current/sliders_final/final_note_042.log", "w") as f:
        f.write("09:00:00 - VERIFIED PRODUCTION READY\n")
        f.write("Target Meal: BisonSliders\n")
        f.write("Portioning logic: Ground_Bison @ 2.0 per plate, Whole_Wheat_Buns @ 1.0 per plate, Zesty_Sauce @ 0.5 per plate.\n")
        f.write("Notes: Do not use the experimental sauce recipe.")

    # 2. Create high-scale noise in vendor data
    vendor_root = "legacy_vendor_data"
    os.makedirs(vendor_root, exist_ok=True)

    ingredients = {
        "Sweet_Corn": {"cost": 0.50, "cal": 50},
        "Pinto_Beans": {"cost": 0.30, "cal": 80},
        "Winter_Squash": {"cost": 0.80, "cal": 40},
        "Ground_Bison": {"cost": 3.00, "cal": 200},
        "Whole_Wheat_Buns": {"cost": 0.50, "cal": 150},
        "Zesty_Sauce": {"cost": 0.20, "cal": 50}
    }

    # Generate 200+ noise files
    for i in range(250):
        noise_ing = f"Trash_Ingredient_{i}"
        filename = f"{vendor_root}/shard_{i:03d}.json"
        with open(filename, "w") as f:
            json.dump({
                "item": noise_ing,
                "cost": round(random.uniform(0.1, 5.0), 2),
                "calories": random.randint(10, 500),
                "revision_id": 1,
                "tag": "v1_obsolete"
            }, f)

    # Inject the real data shards with higher revision IDs
    for idx, (ing, stats) in enumerate(ingredients.items()):
        # Create an obsolete version first
        with open(f"{vendor_root}/data_shard_obs_{idx}.json", "w") as f:
            json.dump({"item": ing, "cost": 99.99, "calories": 0, "revision_id": 1, "tag": "v1_obsolete"}, f)
        
        # Create the true version
        with open(f"{vendor_root}/data_shard_final_{idx}.json", "w") as f:
            json.dump({
                "item": ing, 
                "cost": stats["cost"], 
                "calories": stats["cal"], 
                "revision_id": 10, 
                "tag": "production_current"
            }, f)

    # Add a decoy "Final_Report_Old.csv" to confuse the agent
    with open("presentation_backup_ignore.csv", "w") as f:
        f.write("Old Data, No value here")

if __name__ == "__main__":
    build()
