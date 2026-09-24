import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    os.makedirs("fragments", exist_ok=True)
    os.makedirs("supplier_dump", exist_ok=True)
    os.makedirs("kitchen_prep", exist_ok=True)

    # 1. Ingredient Mapping (Aliases)
    mapping = {
        "Green_Gold": "OrganicAvocado",
        "Starch_Stick": "Plantain",
        "Protein_P": "Pork",
        "Sea_Pink": "Shrimp",
        "Flavor_Gold": "Saffron",
        "Bulb_G": "Garlic"
    }
    with open("mapping_v2.json", "w") as f:
        json.dump(mapping, f)

    # 2. Supplier Data (Fragmentation & Scale)
    ingredients = {
        "Plantain": {"cost": 0.5, "carbon": 1.0},
        "BlackBeans": {"cost": 0.2, "carbon": 0.5},
        "Pork": {"cost": 3.0, "carbon": 10.0},
        "Chicken": {"cost": 2.0, "carbon": 5.0},
        "Rice": {"cost": 0.3, "carbon": 1.2},
        "OrganicAvocado": {"cost": 2.5, "carbon": 2.0},
        "Garlic": {"cost": 0.1, "carbon": 0.1},
        "Onion": {"cost": 0.2, "carbon": 0.2},
        "Shrimp": {"cost": 4.0, "carbon": 6.0},
        "Saffron": {"cost": 10.0, "carbon": 0.1}
    }

    base_date = datetime(2023, 1, 1)
    for i in range(200):  # Generate 200 noise files
        ing_name = random.choice(list(ingredients.keys()))
        rand_date = base_date + timedelta(days=random.randint(0, 100))
        with open(f"supplier_dump/quote_{i:03d}.json", "w") as f:
            json.dump({
                "item": ing_name,
                "cost": round(random.uniform(5.0, 20.0), 2),
                "carbon": round(random.uniform(5.0, 20.0), 2),
                "effective_date": rand_date.strftime("%Y-%m-%d")
            }, f)

    # Inject the "Real" latest data
    latest_date = "2023-12-31"
    for name, stats in ingredients.items():
        with open(f"supplier_dump/final_ref_{name}.json", "w") as f:
            json.dump({
                "item": name,
                "cost": stats["cost"],
                "carbon": stats["carbon"],
                "effective_date": latest_date
            }, f)

    # 3. Recipes (Fragmentation & Decoys)
    recipes_raw = [
        {"name": "Traditional_Lechon", "items": {"Protein_P": 3, "Bulb_G": 5, "Onion": 2}}, # Cost: 9+0.5+0.4=9.9, Carbon: 30+0.5+0.4=30.9
        {"name": "Eco_Plantain_Bowl", "items": {"Starch_Stick": 4, "BlackBeans": 3, "Rice": 2, "Green_Gold": 1}}, # Cost: 2+0.6+0.6+2.5=5.7, Carbon: 4+1.5+2.4+2=9.9 (WINNER)
        {"name": "Fancy_Seafood_Paella", "items": {"Sea_Pink": 5, "Rice": 3, "Flavor_Gold": 1}}, # Cost: 20+0.9+10=30.9 (Over budget)
        {"name": "Chicken_Mojo", "items": {"Chicken": 3, "Bulb_G": 4, "Onion": 2, "Rice": 2}} # Cost: 6+0.4+0.4+0.6=7.4, Carbon: 15+0.4+0.4+2.4=18.2
    ]

    for idx, r in enumerate(recipes_raw):
        # Valid fragment
        with open(f"fragments/rec_{idx}_active.log", "w") as f:
            f.write(f"[STABLE VERSION]\nRecipe: {r['name']}\n")
            for item, qty in r['items'].items():
                f.write(f"Add {qty} units of {item}\n")
        
        # Noise fragment (VOID)
        with open(f"fragments/rec_{idx}_old.tmp", "w") as f:
            f.write("[VOID] DEPRECATED DATA\n")
            f.write(f"Recipe: {r['name']}_OLD\nIngredients: Ghost_Pepper: 100")

    # 4. Pure Noise Files
    for i in range(50):
        with open(f"fragments/junk_{i}.txt", "w") as f:
            f.write("Just some kitchen noise... chop chop chop.")

if __name__ == "__main__":
    build_env()
