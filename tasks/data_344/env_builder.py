import os
import json

def build_env():
    asset_dir = "assets/data_344"
    os.makedirs(asset_dir, exist_ok=True)

    prices = {
        "Tofu": 2.50,
        "Doubanjiang": 3.00,
        "Ground Pork": 5.00,
        "Garlic": 0.50,
        "Sichuan Peppercorn": 1.50,
        "Tomato": 2.00,
        "Egg": 1.50,
        "Scallion": 0.50,
        "Oil": 0.20,
        "Salt": 0.10,
        "Abalone": 50.00,
        "Sea Cucumber": 40.00,
        "Scallop": 20.00,
        "Quail Egg": 5.00,
        "Pork Belly": 8.00,
        "Soy Sauce": 1.20,
        "Rock Sugar": 1.00,
        "Star Anise": 0.50,
        "Ginger": 0.50
    }

    with open(os.path.join(asset_dir, "prices.json"), "w", encoding="utf-8") as f:
        json.dump(prices, f, indent=2)

    raw_recipes = """
-- Grandma's Notes --
Some of these are too expensive now.

[Recipe: Mapo Tofu]
Ingredients: Tofu, Doubanjiang, Ground Pork, Garlic, Sichuan Peppercorn
Notes: Very spicy!

!!! IGNORE THIS JUNK !!!

[Recipe: Tomato Egg Stir-fry]
Ingredients: Tomato, Egg, Scallion, Oil, Salt
Notes: Kid loves this.

[Recipe: Buddha Jumps Over the Wall]
Ingredients: Abalone, Sea Cucumber, Scallop, Quail Egg
Notes: For Chinese New Year only. Too expensive!

[Recipe: Hong Shao Rou]
Ingredients: Pork Belly, Soy Sauce, Rock Sugar, Star Anise, Ginger
Notes: Braised pork belly. Slow cook for 2 hours.
"""
    with open(os.path.join(asset_dir, "raw_recipes.txt"), "w", encoding="utf-8") as f:
        f.write(raw_recipes)

if __name__ == "__main__":
    build_env()
