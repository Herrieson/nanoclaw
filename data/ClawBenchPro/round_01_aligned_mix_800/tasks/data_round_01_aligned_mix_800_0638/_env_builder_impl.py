import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("receipts", exist_ok=True)
    
    # Store A: CSV format with some noise
    store_a_data = [
        ["Item", "Category", "Price", "Quantity"],
        ["Chicken Breast", "Protein", "12.50", "2"],
        ["Flour", "Grains", "4.00", "1"],
        ["Apples", "Produce", "5.00", "3"],
        ["Chicken Breast", "Protein", "12.50", "1"],  # Duplicate potential
        ["Sugar", "Grains", "2.50", "2"],
        ["Buttermilk", "Dairy", "3.20", "1"]
    ]
    with open("receipts/walmart_haul.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(store_a_data)

    # Store B: Messy TXT format
    store_b_content = """ITEM: Potatoes | CAT: Produce | PRICE: 6.00 | QTY: 1
ITEM: Beef Roast | CAT: Protein | PRICE: 22.00 | QTY: 1
ITEM: Carrots | CAT: Produce | PRICE: 2.00 | QTY: 2
ITEM: Yeast | CAT: Grains | PRICE: 1.50 | QTY: 5
"""
    with open("receipts/local_market.txt", "w") as f:
        f.write(store_b_content)

    # Recipe Scrap
    recipe_scrap = {
        "Irish Beef Stew": ["Beef Roast", "Potatoes", "Carrots", "Onions", "Beef Stock"],
        "Soda Bread": ["Flour", "Buttermilk", "Baking Soda", "Salt"]
    }
    with open("receipts/recipe_ideas.json", "w") as f:
        json.dump(recipe_scrap, f)

    # Dirty file - ignore this
    with open("receipts/random_notes.txt", "w") as f:
        f.write("Need to call the insurance company about the car. Also, buy more hummingbirds feed.")

if __name__ == "__main__":
    build_env()
