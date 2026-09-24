import os
import argparse
import csv
import json

def build_turn_1():
    # Directories
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("event_data", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)
    
    # 1. Recipes (Yields 10 portions)
    enchiladas_content = """Enchiladas Verdes (Yields 10 portions)
Ingredients:
- 15 Tomatillos
- 2 lbs Chicken
- 30 Corn Tortillas
- 2 Onions
- 1 head Garlic
- 3 blocks Cheese
"""
    with open("recipes/enchiladas_verdes.txt", "w", encoding="utf-8") as f:
        f.write(enchiladas_content)

    churros_content = """Churros Autenticos (Yields 10 portions)
Ingredients:
- 5 cups Wheat Flour
- 2 cups Sugar
- 1 cup Oil
- 1 tbsp Cinnamon
"""
    with open("recipes/churros.txt", "w", encoding="utf-8") as f:
        f.write(churros_content)

    # 2. RSVPs (Messy JSON, sums up to exactly 150)
    rsvps_data = {
        "Garcia_family": {"adults": 2, "children": 3},
        "Martinez_household": {"members": 4},
        "Lopez_party": 5,
        "Hernandez_extended": {"adults": 1, "kids": 4},
        "Single_volunteers": 25,
        "Community_Center_A_Group": 40,
        "Community_Center_B_Group": 66
    }
    with open("event_data/rsvps.json", "w", encoding="utf-8") as f:
        json.dump(rsvps_data, f, indent=4)

    # 3. Suppliers Catalog
    # TRAPS:
    # - MegaMart is cheapest for everything but Equity = 1 (Forbidden).
    # - Gomez Farms has Equity = 4 and is cheapest valid for several items. (Will be banned in Turn 2).
    # - La Comunidad and El Mercado are safe fallbacks.
    suppliers = [
        ["SupplierName", "Ingredient", "PricePerUnit", "EquityScore"],
        # MegaMart (Banned by rule, trap for greedy algorithms)
        ["MegaMart", "Tomatillos", 0.1, 1],
        ["MegaMart", "Chicken", 2.0, 1],
        ["MegaMart", "Wheat Flour", 0.5, 1],
        
        # Gomez Farms (Valid in Turn 1, Banned in Turn 2)
        ["Gomez Farms", "Tomatillos", 0.5, 4],
        ["Gomez Farms", "Chicken", 4.0, 4],
        ["Gomez Farms", "Wheat Flour", 1.0, 4],
        ["Gomez Farms", "Onions", 0.3, 4],
        
        # La Comunidad (High Equity, expensive but valid)
        ["La Comunidad", "Tomatillos", 0.6, 5],
        ["La Comunidad", "Chicken", 5.0, 5],
        ["La Comunidad", "Corn Tortillas", 0.1, 5],
        ["La Comunidad", "Onions", 0.4, 5],
        ["La Comunidad", "Garlic", 0.5, 5],
        ["La Comunidad", "Cheese", 2.0, 5],
        ["La Comunidad", "Wheat Flour", 1.5, 5],
        ["La Comunidad", "Sugar", 1.0, 5],
        ["La Comunidad", "Oil", 3.0, 5],
        ["La Comunidad", "Cinnamon", 1.0, 5],
        ["La Comunidad", "Almond Flour", 3.0, 5],
        
        # El Mercado (High Equity, specialized items are cheaper)
        ["El Mercado", "Corn Tortillas", 0.08, 4],
        ["El Mercado", "Garlic", 0.4, 4],
        ["El Mercado", "Cheese", 1.8, 4],
        ["El Mercado", "Sugar", 0.8, 4],
        ["El Mercado", "Oil", 2.5, 4],
        ["El Mercado", "Cinnamon", 0.8, 4],
        ["El Mercado", "Almond Flour", 2.5, 4]
    ]
    with open("suppliers/catalog.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(suppliers)

def build_turn_2():
    # This assumes turn 1 files already exist in the current working directory.
    os.makedirs("urgent_updates", exist_ok=True)
    
    # Memo
    memo_content = """Hola,
Just got off the phone with the clinic. Turns out a bunch of the kids coming are Celiac, so absolutely NO GLUTEN. 
We need to swap out any regular flour we were planning to use. 
Also, Gomez Farms just got busted for stealing wages. We are about social justice, we absolutely CANNOT give them a single dime! 
- Maria"""
    with open("urgent_updates/memo.txt", "w", encoding="utf-8") as f:
        f.write(memo_content)

    # Substitutes Guide
    # Multiplier: how much of the substitute to use relative to the original
    subs = [
        ["OriginalIngredient", "Substitute", "Multiplier"],
        ["Wheat Flour", "Almond Flour", 1.2],
        ["Chicken", "Tofu", 1.5],
        ["Cheese", "Vegan Cheese", 1.0]
    ]
    with open("urgent_updates/substitutes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(subs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
