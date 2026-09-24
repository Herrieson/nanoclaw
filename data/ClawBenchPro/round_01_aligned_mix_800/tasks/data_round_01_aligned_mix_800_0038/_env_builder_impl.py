import os
import json
import csv
import yaml
import argparse

def create_recipe_json(path, name, portions, ingredients, allergens):
    with open(path, 'w') as f:
        json.dump({
            "recipe_name": name,
            "portions": portions,
            "ingredients": ingredients,
            "allergens": allergens
        }, f, indent=2)

def create_recipe_xml(path, name, portions, ingredients, allergens):
    xml_content = f"<recipe>\n  <name>{name}</name>\n  <portions>{portions}</portions>\n  <ingredients>\n"
    for k, v in ingredients.items():
        xml_content += f'    <item name="{k}" qty="{v}"/>\n'
    xml_content += "  </ingredients>\n  <allergens>\n"
    for a in allergens:
        xml_content += f'    <allergen>{a}</allergen>\n'
    xml_content += "  </allergens>\n</recipe>"
    with open(path, 'w') as f:
        f.write(xml_content)

def create_recipe_txt(path, name, portions, ingredients, allergens):
    txt = f"Recipe: {name}\nPortions: {portions}\nIngredients:\n"
    for k, v in ingredients.items():
        txt += f"- {k}: {v}\n"
    txt += "Allergens: " + (", ".join(allergens) if allergens else "none") + "\n"
    with open(path, 'w') as f:
        f.write(txt)

def build_turn_1():
    os.makedirs("community", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("recipe_box", exist_ok=True)
    os.makedirs("plans", exist_ok=True)
    os.makedirs("events", exist_ok=True)

    # Neighbors: Total 9 people.
    neighbors = [
        {"name": "Smith", "family_size": 4, "allergies": ["peanuts"]},
        {"name": "Johnson", "family_size": 3, "allergies": ["gluten"]},
        {"name": "Davis", "family_size": 2, "allergies": []}
    ]
    with open("community/neighbors.json", "w") as f:
        json.dump(neighbors, f, indent=2)

    # Pantry
    pantry_data = [
        ["item", "qty", "unit_price"],
        ["chicken", 2, 5.0],
        ["beef", 1, 8.0],
        ["pork", 1, 6.0],
        ["lentils", 10, 1.0],
        ["pasta", 5, 2.0],
        ["tomato", 5, 1.0],
        ["cheese", 2, 3.0],
        ["flour", 5, 1.0],
        ["rice", 2, 2.0],
        ["beans", 2, 1.5],
        ["peanuts", 5, 1.0]
    ]
    with open("inventory/pantry.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(pantry_data)

    # Recipes
    # Trap 1: Peanut Stew. Very cheap, feeds 5. But Smith has peanut allergy.
    create_recipe_json("recipe_box/R01_Peanut_Stew.json", "Peanut Stew", 5, {"chicken": 1, "peanuts": 2}, ["peanuts"])
    
    # Valid for Turn 1: Lentil Soup. Feeds 5. Needs 5 lentils, 2 tomatoes. (Batch cost: $7. Pantry has plenty).
    create_recipe_txt("recipe_box/R02_Lentil_Soup.txt", "Lentil Soup", 5, {"lentils": 5, "tomato": 2}, [])
    
    # Valid for Turn 1: Chicken Pasta. Feeds 5. Needs 1 chicken, 2 pasta. (Batch cost: $9). 
    create_recipe_xml("recipe_box/R03_Chicken_Pasta.xml", "Chicken Pasta", 5, {"chicken": 1, "pasta": 2}, ["gluten_free_actually"])
    
    # Trap 2: Beef Roast. Feeds 5. Needs 3 beef. ($24 per batch. Need 2 batches = $48. Too expensive for week 1 budget).
    create_recipe_json("recipe_box/R04_Beef_Roast.json", "Beef Roast", 5, {"beef": 3, "tomato": 1}, [])
    
    # Valid for Turn 1: Cheese Veggie Bake. Feeds 3. Needs 1 cheese, 1 tomato. (Batch cost: $4).
    create_recipe_txt("recipe_box/R05_Veggie_Bake.txt", "Veggie Bake", 3, {"cheese": 1, "tomato": 1}, [])
    
    # Trap for Turn 2: Shrimp Paella. Feeds 6. Needs 2 rice, 2 shrimp ($5 ea).
    create_recipe_xml("recipe_box/R06_Shrimp_Paella.xml", "Shrimp Paella", 6, {"rice": 2, "shrimp": 2}, ["shellfish"])
    
    # Final Boss (Turn 3) valid recipe: Pork & Bean Rice. Feeds 12. Needs 2 pork, 5 rice, 5 beans.
    create_recipe_json("recipe_box/R07_Pork_Fiesta.json", "Pork Fiesta", 12, {"pork": 2, "rice": 5, "beans": 5}, [])
    
    # Trap for Johnson: Gluten Macaroni.
    create_recipe_txt("recipe_box/R08_Gluten_Mac.txt", "Gluten Mac", 4, {"pasta": 2, "cheese": 2}, ["gluten"])

    # Valid for Turn 2: Chicken Rice. Feeds 6. Needs 1 chicken, 2 rice. 
    create_recipe_xml("recipe_box/R09_Chicken_Rice.xml", "Chicken Rice", 6, {"chicken": 1, "rice": 2}, [])

    # Valid for Turn 2: Bean Soup. Feeds 4. Needs 3 beans, 1 tomato.
    create_recipe_json("recipe_box/R10_Bean_Soup.json", "Bean Soup", 4, {"beans": 3, "tomato": 1}, [])


def build_turn_2():
    # Injected events
    with open("events/flood_damage.txt", "w") as f:
        f.write("Disaster!\nThe water ruined the following items completely. DO NOT use them from the pantry:\n- lentils\n- pasta\n")
    
    new_arrivals = [
        ["name", "family_size", "allergies"],
        ["Miller", 2, "shellfish"]
    ]
    with open("community/new_arrivals.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_arrivals)


def build_turn_3():
    donations = {
        "donated_items": [
            {"item": "pork", "qty": 3},
            {"item": "rice", "qty": 8},
            {"item": "beans", "qty": 10},
            {"item": "tomato", "qty": 5}
        ]
    }
    with open("events/church_donations.yaml", "w") as f:
        yaml.dump(donations, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
