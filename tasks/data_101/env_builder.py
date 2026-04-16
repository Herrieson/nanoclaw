import os
import json
import sqlite3

def build_env():
    base_dir = os.path.join("assets", "data_101")
    recipes_dir = os.path.join(base_dir, "recipes")
    os.makedirs(recipes_dir, exist_ok=True)
    os.makedirs(os.path.join(recipes_dir, "old_stuff"), exist_ok=True)
    os.makedirs(os.path.join(recipes_dir, "new_ideas"), exist_ok=True)

    # 1. Standard JSON format
    recipe1 = {
        "name": "Bratwurst Tacos",
        "tags": ["fusion", "german", "mexican"],
        "ingredients": {"bratwurst": 2, "tortilla": 3, "salsa": 1}
    }
    with open(os.path.join(recipes_dir, "new_ideas", "german_mex.json"), "w") as f:
        json.dump(recipe1, f)

    # 2. Heterogeneous JSON format (different keys to test parsing robustness)
    recipe2 = {
        "title": "Soul Food Ramen",
        "categories": ["experimental", "comfort"],
        "items": {"ramen_noodles": 1, "collard_greens": 2, "pork_belly": 1}
    }
    with open(os.path.join(recipes_dir, "old_stuff", "ramen_idea.json"), "w") as f:
        json.dump(recipe2, f)

    # 3. Distractor JSON (should be ignored based on tags)
    recipe3 = {
        "name": "Classic Cheeseburger",
        "tags": ["classic", "american"],
        "ingredients": {"beef_patty": 1, "bun": 1, "cheese": 1}
    }
    with open(os.path.join(recipes_dir, "burger.json"), "w") as f:
        json.dump(recipe3, f)

    # 4. Unstructured Text File (requires regex or NLP parsing)
    text_recipe = """
Just had a crazy idea while humming that jazz tune. 
Recipe Name: Spicy Schnitzel
tags: experimental, spicy
ingredients: pork_cutlet 1, hot_sauce 2, breadcrumbs 1
Gotta try this for the kids!
"""
    with open(os.path.join(recipes_dir, "notes.txt"), "w") as f:
        f.write(text_recipe)

    # 5. Build SQLite Database for pricing
    db_path = os.path.join(base_dir, "supplier.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE prices (
            ingredient TEXT PRIMARY KEY,
            unit_price REAL
        )
    ''')
    
    prices = [
        ("bratwurst", 1.5),
        ("tortilla", 0.2),
        ("salsa", 0.5),
        ("ramen_noodles", 0.8),
        ("collard_greens", 1.0),
        ("pork_belly", 2.5),
        ("beef_patty", 2.0),
        ("bun", 0.5),
        ("cheese", 0.3),
        ("pork_cutlet", 2.0),
        ("hot_sauce", 0.3),
        ("breadcrumbs", 0.4)
    ]
    
    cursor.executemany('INSERT INTO prices VALUES (?, ?)', prices)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
