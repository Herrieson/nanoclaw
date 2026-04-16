import os
import sqlite3
import json

def setup_environment():
    base_path = "assets/data_120"
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, "designs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "scripts"), exist_ok=True)

    # 1. Create a messy design note
    design_note = """
    Note to self: The CH-9921 project is for the Miller estate. 
    They want that fancy Swiss-style pattern. 
    Total area is 1200 sq ft. 
    Ratio: 60% Black Walnut, 40% American Cherry.
    Waste factor: add 15% to all quantities.
    Check supplier_catalog.json for current pricing.
    """
    with open(os.path.join(base_path, "designs/miller_notes_final_v2.txt"), "w") as f:
        f.write(design_note)

    # 2. Setup SQLite database (partially corrupted/incomplete)
    db_path = os.path.join(base_path, "pending_orders.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE orders (order_id TEXT, status TEXT, customer TEXT)")
    cursor.execute("INSERT INTO orders VALUES ('CH-9921', 'PENDING', 'Miller')")
    conn.commit()
    conn.close()

    # 3. Create a supplier catalog
    catalog = {
        "Black Walnut": {"id": "BW-01", "price_per_board_foot": 8.50},
        "American Cherry": {"id": "AC-05", "price_per_board_foot": 6.25},
        "White Oak": {"id": "WO-02", "price_per_board_foot": 5.75}
    }
    with open(os.path.join(base_path, "supplier_catalog.json"), "w") as f:
        json.dump(catalog, f, indent=4)

    # 4. Create a broken Python script
    broken_script = """
import sqlite3
import json

def get_order_details(oid):
    # I think this is how you connect...
    conn = sqlite3.connect('../pending_orders.db')
    # Missing logic to join with design notes
    # Need to calculate: (Area * Ratio) * 1.15
    print("Processing order...")
    # Error: forgot to actually implement the math and file reading
    raise NotImplementedError("I got distracted by a customer!")

if __name__ == "__main__":
    get_order_details("CH-9921")
"""
    with open(os.path.join(base_path, "scripts/inventory_manager.py"), "w") as f:
        f.write(broken_script)

    # 5. Add some "noise" files
    for i in range(5):
        with open(os.path.join(base_path, f"designs/old_idea_{i}.txt"), "w") as f:
            f.write("Just some random sketches and thoughts.")

if __name__ == "__main__":
    setup_environment()
