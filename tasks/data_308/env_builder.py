import os
import sqlite3

def build_env():
    base_dir = "assets/data_308"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "notes"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "notes/random"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "notes/old"), exist_ok=True)

    # Create database
    db_path = os.path.join(base_dir, "planner.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE materials (id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("CREATE TABLE crafts (id INTEGER PRIMARY KEY, name TEXT, eco_points INTEGER, material_id INTEGER)")

    materials = [
        (1, "Recycled Cardboard"),
        (2, "Plastic Bottles"), # Contains "Plastic"
        (3, "Organic Cotton"),
        (4, "Glitter and Glue"), # Contains "Glitter"
        (5, "Pinecones")
    ]
    c.executemany("INSERT INTO materials VALUES (?, ?)", materials)

    crafts = [
        (1, "Cardboard Castle", 50, 1),
        (2, "Bottle Planter", 20, 2), # Exclude
        (3, "Cotton Friendship Bracelets", 30, 3),
        (4, "Sparkly Ornaments", 10, 4), # Exclude
        (5, "Pinecone Animals", 40, 5)
    ]
    c.executemany("INSERT INTO crafts VALUES (?, ?, ?, ?)", crafts)
    conn.commit()
    conn.close()

    # Create text files
    text1 = """
Idea 1: Leaf Art
Points: 25
Materials: Leaves, Paper

Idea 2: Brillantina Slime
Points: 15
Materials: Slime, brillantina, water
"""
    with open(os.path.join(base_dir, "notes", "monday.txt"), "w") as f:
        f.write(text1.strip())

    text2 = """
Some other ideas for the kiddos:

- Name: Acorn People
- Points: 35
- Materials: Acorns, markers

- Name: Plastico Wind Chime
- Points: 10
- Materials: plastico cups, string
"""
    with open(os.path.join(base_dir, "notes/random", "ideas.log"), "w") as f:
        f.write(text2.strip())

    text3 = """
- Name: Rock Painting
- Points: 20
- Materials: Rocks, eco-paint
"""
    with open(os.path.join(base_dir, "notes/old", "spanglish.md"), "w") as f:
        f.write(text3.strip())

if __name__ == "__main__":
    build_env()
