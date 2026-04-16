import os
import sqlite3
import base64

def build_env():
    base_dir = "assets/data_227"
    os.makedirs(base_dir, exist_ok=True)

    db_path = os.path.join(base_dir, "inventory.db")
    
    # Remove if exists to ensure clean state
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE products (
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    category TEXT, 
                    price REAL, 
                    details_b64 TEXT
                 )''')

    # Data to insert
    products = [
        (101, "Ergo Chair Pro", "Seating", 299.99, "ergonomic, bamboo, natural_oil"),
        (102, "Budget Sofa", "Seating", 199.50, "plywood, formaldehyde, polyester"),
        (103, "Organic Mattress", "Sleep", 899.00, "organic_cotton, natural_latex, ergonomic"),
        (104, "Basic Bed Frame", "Sleep", 150.00, "pine, synthetic_voc, metal"),
        (105, "Yoga Mat Stand", "Accessories", 45.00, "bamboo, eco_friendly"),
        (106, "Standing Desk", "Desks", 450.00, "bamboo, ergonomic"),
        (107, "Meditation Cushion", "Seating", 85.00, "buckwheat, organic_cotton"),
        (108, "Memory Foam Pillow", "Sleep", 60.00, "polyurethane, synthetic_voc"),
        (109, "Lounge Recliner", "Seating", 350.00, "leather, ergonomic, safe_dye"),
        (110, "Cheap Nightstand", "Sleep", 40.00, "mdf, formaldehyde, paint")
    ]

    for p in products:
        # Base64 encode the details string to simulate the "weird IT system" encoding
        details_encoded = base64.b64encode(p[4].encode('utf-8')).decode('utf-8')
        c.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?)", (p[0], p[1], p[2], p[3], details_encoded))

    conn.commit()
    conn.close()

    # Create manager's notes
    notes_content = """Hey,
For your wellness collection display, please stick to the following constraints:
- Categories to include: ONLY 'Seating' and 'Sleep'. We don't have space for anything else.
- Exclude ANY item if its details contain the words 'formaldehyde' or 'synthetic_voc'. Legal says we can't associate those with wellness.
- IT says the details column in inventory.db is base64 encoded now, so you'll have to decode it first before you search the text.

Create a file named 'wellness_budget.txt' in this directory.
- Line 1: A comma-separated list of the selected product IDs (in ascending order).
- Line 2: The total sum of their prices (just the number, formatted to 2 decimal places).

Get this to me by EOD.
"""
    with open(os.path.join(base_dir, "manager_notes.txt"), "w", encoding="utf-8") as f:
        f.write(notes_content)

if __name__ == "__main__":
    build_env()
