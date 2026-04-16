import os
import sqlite3

def build_env():
    base_dir = "assets/data_438"
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "kitchen.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE ingredients (
            id INTEGER PRIMARY KEY,
            name TEXT,
            stock REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE recipe_ingredients (
            recipe_id INTEGER,
            ingredient_id INTEGER,
            amount_per_serving REAL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id),
            FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
        )
    """)
    
    # Insert ingredients
    ingredients = [
        (1, 'Bratwurst', 10.0),
        (2, 'Rice', 500.0),
        (3, 'Shrimp', 20.0),
        (4, 'Pork Loin', 5.0),
        (5, 'Tortillas', 12.0),
        (6, 'Sauerkraut', 100.0),
        (7, 'Plantains', 4.0),
        (8, 'Beef', 10.0),
        (9, 'Empanada Dough', 0.0),
        (10, 'Tomato Sauce', 15.0)
    ]
    cursor.executemany("INSERT INTO ingredients VALUES (?, ?, ?)", ingredients)
    
    # Insert recipes
    recipes = [
        (1, 'Bratwurst Jambalaya'),
        (2, 'Schnitzel Tacos'),
        (3, 'Sauerkraut Empanadas'),
        (4, 'Normal Spaghetti'),
        (5, 'Boring Salad')
    ]
    cursor.executemany("INSERT INTO recipes VALUES (?, ?)", recipes)
    
    # Insert recipe_ingredients
    recipe_ingredients = [
        # Bratwurst Jambalaya
        (1, 1, 0.5),
        (1, 2, 50.0),
        (1, 3, 2.0),
        # Schnitzel Tacos
        (2, 4, 0.2),
        (2, 5, 3.0),
        (2, 6, 10.0),
        # Sauerkraut Empanadas
        (3, 6, 15.0),
        (3, 9, 2.0),
        (3, 7, 0.5),
        # Normal Spaghetti
        (4, 8, 0.2),
        (4, 10, 1.0)
    ]
    cursor.executemany("INSERT INTO recipe_ingredients VALUES (?, ?, ?)", recipe_ingredients)
    
    conn.commit()
    conn.close()
    
    # Write ramblings.txt
    ramblings_content = """Man, today was wild. The kids were begging to go to the climbing gym, so we spent like three hours there. I'm exhausted. Hmm hmm hmm... 🎵 what was that tune again? 
Anyway, when we got back I whipped up some Bratwurst Jambalaya. Total fusion dish, right? Classic me bringing the German and the Southern together. The kids actually loved it!
Then I'm planning Schnitzel Tacos for tomorrow. Another crazy fusion idea that actually works! My buddy asked for the recipe for Sauerkraut Empanadas too, definitely gonna count that in my fusion lineup for the neighborhood party. 
Made Normal Spaghetti for the kids later, but that's just normal food. Gotta remember to pick up more stuff for the party. My head is all over the place today."""
    
    with open(os.path.join(base_dir, "ramblings.txt"), "w") as f:
        f.write(ramblings_content)

if __name__ == "__main__":
    build_env()
