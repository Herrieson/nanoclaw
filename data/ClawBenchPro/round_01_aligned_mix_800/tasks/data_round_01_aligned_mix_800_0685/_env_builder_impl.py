import os
import csv

def build_env():
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("kitchen_prep", exist_ok=True)

    suppliers_data = [
        ["Ingredient", "CostPerUnit", "CarbonFootprintPerUnit"],
        ["Plantain", "0.5", "1.0"],
        ["BlackBeans", "0.2", "0.5"],
        ["Pork", "3.0", "10.0"],
        ["Chicken", "2.0", "5.0"],
        ["Rice", "0.3", "1.2"],
        ["OrganicAvocado", "2.5", "2.0"],
        ["Garlic", "0.1", "0.1"],
        ["Onion", "0.2", "0.2"],
        ["Shrimp", "4.0", "6.0"],
        ["Saffron", "10.0", "0.1"]
    ]

    with open("suppliers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(suppliers_data)

    recipe_1 = """Recipe: Traditional_Lechon
Man, this is a classic, but meat is heavy on the earth.
Ingredients:
- Pork: 3
- Garlic: 5
- Onion: 2
"""
    with open("recipes/Traditional_Lechon.txt", "w") as f:
        f.write(recipe_1)

    recipe_2 = """Recipe: Eco_Plantain_Bowl
This one is my favorite experiment! Super green and fresh.
Ingredients:
- Plantain: 4
- BlackBeans: 3
- Rice: 2
- OrganicAvocado: 1
"""
    with open("recipes/Eco_Plantain_Bowl.txt", "w") as f:
        f.write(recipe_2)

    recipe_3 = """Recipe: Fancy_Seafood_Paella
Boss might like this, but saffron is crazy expensive.
Ingredients:
- Shrimp: 5
- Rice: 3
- Saffron: 1
"""
    with open("recipes/Fancy_Seafood_Paella.txt", "w") as f:
        f.write(recipe_3)

    recipe_4 = """Recipe: Chicken_Mojo
A safe bet, everyone loves chicken.
Ingredients:
- Chicken: 3
- Garlic: 4
- Onion: 2
- Rice: 2
"""
    with open("recipes/Chicken_Mojo.txt", "w") as f:
        f.write(recipe_4)

if __name__ == "__main__":
    build_env()
