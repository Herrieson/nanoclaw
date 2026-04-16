import os
import json
import csv

def build_env():
    base_dir = "assets/data_03/trip_prep"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Messy recipes note
    recipes_content = """
    Weekend Menu Notes!!
    
    Meal 1: Bratwurst Fusion Tacos
    - Need 5 sausages. (German style!)
    - 10 tortillas.
    - 1 jar of mustard. 
    - 2 lbs of beef. (for the chili topping)
    - 1 jar of salsa.
    *hmmm hmmm da da dum*
    
    Meal 2: Kids' favorite weird dogs
    - Need 5 buns.
    - Need 4 more sausages.
    - 1 more jar of salsa.
    
    Wait, did I count the sausages right? Yeah, 5 for meal 1, 4 for meal 2. So 9 total.
    Buns: 5. Tortillas: 10. Mustard: 1. Beef: 2. Salsa: 2.
    """
    with open(os.path.join(base_dir, "recipes.txt"), "w") as f:
        f.write(recipes_content)

    # 2. Pantry inventory (CSV)
    pantry_data = [
        ["item", "quantity_in_stock"],
        ["sausages", "2"],
        ["buns", "12"], # Got plenty of buns
        ["mustard", "1"], # Have 1 jar
        ["tortillas", "0"],
        ["beef", "0"],
        ["salsa", "1"] # Have 1 jar, need 2 total
    ]
    with open(os.path.join(base_dir, "pantry.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(pantry_data)

    # 3. Store prices (JSON)
    prices_data = {
        "sausages": 1.50,
        "buns": 0.50,
        "mustard": 3.00,
        "tortillas": 0.20,
        "beef": 5.00,
        "salsa": 4.00
    }
    with open(os.path.join(base_dir, "prices.json"), "w") as f:
        json.dump(prices_data, f, indent=4)

if __name__ == "__main__":
    build_env()
