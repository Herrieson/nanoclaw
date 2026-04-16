import os
import json

def build_env():
    base_dir = "assets/data_364/hot_sauce_stuff"
    os.makedirs(base_dir, exist_ok=True)

    # 1. peppers.csv
    peppers_csv = """Pepper Name,SHU
Jalapeno,5000
Serrano,15000
Cayenne,50000
Habanero,250000
Ghost Pepper,1000000
Carolina Reaper,2000000
"""
    with open(os.path.join(base_dir, "peppers.csv"), "w") as f:
        f.write(peppers_csv)

    # 2. prices.json
    prices = {
        "Habanero": 2.50,
        "Ghost Pepper": 5.00,
        "Vinegar": 1.00,
        "Salt": 0.50,
        "Jalapeno": 1.00,
        "Tomato Paste": 1.50,
        "Sugar": 1.00,
        "Carolina Reaper": 10.00,
        "Saffron": 35.00,
        "Cayenne": 2.00,
        "Garlic": 1.50,
        "Cheddar": 4.00,
        "Serrano": 1.50
    }
    with open(os.path.join(base_dir, "prices.json"), "w") as f:
        json.dump(prices, f, indent=4)

    # 3. budget.txt
    with open(os.path.join(base_dir, "budget_note.txt"), "w") as f:
        f.write("Wife said we need to save for the kid's preschool. Weekend fun grocery budget is firmly capped at $20.00. Do not go over.")

    # 4. Recipes
    # Recipe 1: Passes (Avg SHU: 625,000. Cost: 9.00)
    recipe1 = """Name: Devil's Tears
Ingredients: Habanero, Ghost Pepper, Vinegar, Salt
Notes: Wear gloves!
"""
    with open(os.path.join(base_dir, "recipe_1.txt"), "w") as f:
        f.write(recipe1)

    # Recipe 2: Fails SHU (Avg SHU: 5000. Cost: 3.50)
    recipe2 = """sauce_name=Wimpy Ketchup
items=Jalapeno,Tomato Paste,Sugar
"""
    with open(os.path.join(base_dir, "recipe_wimpy.log"), "w") as f:
        f.write(recipe2)

    # Recipe 3: Fails Budget (Avg SHU: 1,500,000. Cost: 51.00)
    recipe3 = """# The Bankrupt Burner
* Carolina Reaper
* Saffron
* Ghost Pepper
* Vinegar
"""
    with open(os.path.join(base_dir, "recipe_expensive.md"), "w") as f:
        f.write(recipe3)

    # Recipe 4: Passes (Avg SHU: 150,000. Cost: 7.00)
    recipe4 = """Name: Midwest Meltdown
Ingredients: Cayenne, Habanero, Garlic, Vinegar
"""
    with open(os.path.join(base_dir, "midwest.txt"), "w") as f:
        f.write(recipe4)

if __name__ == "__main__":
    build_env()
