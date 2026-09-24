import os
import json
import csv

def build_env():
    # Create required directories in the current working directory
    os.makedirs("stockroom_logs", exist_ok=True)
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("pos_data", exist_ok=True)

    # 1. Generate Recipes (Reflecting the persona's Irish/Missouri roots)
    recipes = {
        "Irish Sunrise": ["Tequila", "Orange Juice", "Grenadine"],
        "Missouri Mule": ["Vodka", "Ginger Beer", "Lime Juice"],
        "Midwest Fidget": ["Bourbon", "Bitters", "Simple Syrup"]
    }
    with open("recipes/my_ideas.json", "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2)

    # 2. Generate Messy Inventory Data
    # Deliberately dirty data to require parsing/cleaning. 
    # Grenadine and Bourbon are missing/out of stock.
    inventory_content = """
    MORNING SHIFT INVENTORY CHECK - Friday
    --------------------------------------
    - Tequila: 2 bottles (half full)
    - ORANGE juice : 5 liters in walk-in
    - Vodka: 3 btls (premium)
    - ginger beer: 12 cans left
    - Lime Juice: 1 squeezer bottle
    - bitters: 1 bottle at station 2
    - simple syrup: 2 liters homemade
    
    # NOTE FOR DANNY: We are completely out of Grenadine until Tuesday!!
    # NOTE 2: Bourbon is tapped out, didn't get the delivery.
    """
    with open("stockroom_logs/morning_inventory.txt", "w", encoding="utf-8") as f:
        f.write(inventory_content)

    # 3. Generate Messy POS Tip Data
    # Danny's total should be: 
    # 100*0.20(20) + 250*0.20(50) + 50*0.20(10) + 1500*0.18(270) = 350.00
    with open("pos_data/shift_closing.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["TransactionID", "Server", "Bartender_Helper", "Total_Tip", "Helper_Cut_Percentage"])
        writer.writerow(["TX_001", "Sarah", "Danny", "100.00", "20%"])
        writer.writerow(["TX_002", "Mike", "Danny", "250.00", "20%"])
        writer.writerow(["TX_003", "Sarah", "Danny", "50.00", "20%"])
        writer.writerow(["TX_004", "John", "Chris_Morning", "300.00", "20%"]) # Not Danny
        writer.writerow(["TX_005", "Mike", "Danny", "1500.00", "18%"]) # High roller

if __name__ == "__main__":
    build_env()
