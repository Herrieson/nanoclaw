import os
import csv
import json
import random

def build_env():
    random.seed(1669) # Ensure deterministic wasteland

    # 1. Generate fragmented volunteer roster
    os.makedirs("system_export", exist_ok=True)
    os.makedirs("compliance_certs", exist_ok=True)

    roles = ["Serving", "Setup", "Cleanup", "Coordination", "Marketing"]
    statuses = ["Passed", "Pending", "Failed", "Expired", "Revoked"]
    
    with open("system_export/volunteer_dump.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Volunteer_ID", "Full_Name", "Assigned_Role", "Join_Date"])
        
        for i in range(1, 801):
            is_sys_test = random.random() < 0.15
            vol_id = f"SYS_TEST_{i:04d}" if is_sys_test else f"VOL_{i:04d}"
            name = f"Volunteer_{i}"
            role = random.choice(roles)
            writer.writerow([vol_id, name, role, f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"])
            
            # 2. Generate Compliance Certs (Some missing on purpose to test "doesn't have one")
            if random.random() < 0.90:
                cert_status = "Passed" if random.random() < 0.4 else random.choice(statuses)
                cert_data = {
                    "volunteer_id": vol_id,
                    "inspector_id": f"INSP_{random.randint(10,99)}",
                    "status": cert_status,
                    "notes": "System migrated record."
                }
                with open(f"compliance_certs/{vol_id}_record.json", "w", encoding="utf-8") as cf:
                    json.dump(cert_data, cf, indent=2)

    # 3. Generate deeply nested recipe wasteland
    categories = [
        "Traditional Filipino", 
        "Modern Filipino", 
        "Filipino-Fusion", 
        "American Comfort", 
        "Italian", 
        "Mexican Traditional"
    ]
    
    base_ingredients = {
        "Traditional Filipino": ["Pork belly", "Soy sauce", "Vinegar", "Garlic", "Bay leaves", "Tamarind broth", "Water spinach"],
        "Modern Filipino": ["Truffle oil", "Soy sauce", "Vegan pork", "Quinoa"],
        "Filipino-Fusion": ["Adobo seasoning", "Taco shells", "Cheddar cheese", "Cilantro"],
        "American Comfort": ["Macaroni", "Cheese", "Butter", "Milk"],
        "Italian": ["Pasta", "Tomato sauce", "Basil", "Mozzarella"],
        "Mexican Traditional": ["Corn tortillas", "Pork shoulder", "Achiote", "Pineapple"]
    }

    recipe_count = 0
    for year in ["2021", "2022", "2023"]:
        for month in range(1, 13):
            folder_path = os.path.join("global_recipes", year, f"{month:02d}")
            os.makedirs(folder_path, exist_ok=True)
            
            # Generate 2 to 5 recipes per month
            for _ in range(random.randint(2, 5)):
                recipe_count += 1
                cat = random.choice(categories)
                
                # Pick a subset of ingredients based on category
                pool = base_ingredients[cat]
                num_ing = random.randint(2, len(pool))
                ings = random.sample(pool, num_ing)
                
                recipe_data = {
                    "recipe_id": f"REC_{recipe_count:05d}",
                    "name": f"Dish {recipe_count}",
                    "metadata": {
                        "category": cat,
                        "author": f"Chef_{random.randint(1,50)}"
                    },
                    "ingredients": ings,
                    "instructions": "Migrated data, instructions lost."
                }
                
                # Mix up file extensions to add slight noise, though all are JSON formatted
                ext = random.choice([".json", ".txt", ".dat"])
                with open(os.path.join(folder_path, f"recipe_{recipe_count}{ext}"), "w", encoding="utf-8") as rf:
                    json.dump(recipe_data, rf)

if __name__ == "__main__":
    build_env()
