import os
import sqlite3
import json

def build_env():
    base_dir = "assets/data_303"
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "bakery.db")
    
    # Remove if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            servings INTEGER NOT NULL,
            ingredients_json TEXT NOT NULL,
            instructions TEXT
        )
    ''')
    
    # Insert dummy data
    dummy_recipes = [
        {
            "title": "Classic Irish Soda Bread",
            "servings": 8,
            "ingredients_json": json.dumps({"flour": 4, "buttermilk": 2, "salt": 1, "baking_soda": 1}),
            "instructions": "Mix and bake."
        },
        {
            "title": "Sweet Raisin Bread",
            "servings": 6,
            "ingredients_json": json.dumps({"flour": 3, "milk": 1, "raisins": 1, "sugar": 0.5, "cinnamon": 1}),
            "instructions": "Knead well."
        },
        {
            "title": "O'Connor's Special (Wrong)",
            "servings": 4,
            "ingredients_json": json.dumps({"flour": 4, "buttermilk": 1.5, "caraway_seeds": 1, "raisins": 0.5, "lemon_zest": 2, "salt": 1, "baking_soda": 1}),
            "instructions": "Mix dry, add wet."
        },
        {
            "title": "Sunset Bread (The Target)",
            "servings": 4,
            "ingredients_json": json.dumps({
                "flour": 4.0, 
                "buttermilk": 1.5, 
                "caraway_seeds": 1.0, 
                "dried_currants": 0.5, 
                "orange_zest": 2.0, 
                "salt": 1.0, 
                "baking_soda": 1.0
            }),
            "instructions": "Mix dry ingredients. Add buttermilk. Bake at 375F for 45 mins."
        },
        {
            "title": "Lemon Herb Loaf",
            "servings": 10,
            "ingredients_json": json.dumps({"flour": 5, "water": 2, "thyme": 1, "lemon_zest": 3, "olive_oil": 0.5}),
            "instructions": "Proof for 2 hours."
        }
    ]
    
    for r in dummy_recipes:
        cursor.execute('''
            INSERT INTO recipes (title, servings, ingredients_json, instructions)
            VALUES (?, ?, ?, ?)
        ''', (r["title"], r["servings"], r["ingredients_json"], r["instructions"]))
    
    conn.commit()
    conn.close()
    
    print(f"Environment built successfully at {base_dir}")

if __name__ == "__main__":
    build_env()
