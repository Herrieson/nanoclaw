import os
import json
import csv

def build_env():
    base_dir = "assets/data_393"
    os.makedirs(base_dir, exist_ok=True)
    
    recipes_dir = os.path.join(base_dir, "recipes")
    os.makedirs(recipes_dir, exist_ok=True)
    
    # Recipe 1
    with open(os.path.join(recipes_dir, "saffron_risotto.txt"), "w") as f:
        f.write("VIP Saffron Risotto\n")
        f.write("Ingredients needed:\n")
        f.write("- Saffron: 5 grams\n")
        f.write("- Arborio Rice: 1000 grams\n")
        f.write("- Parmesan: 150 grams\n")

    # Recipe 2
    with open(os.path.join(recipes_dir, "truffle_pasta.txt"), "w") as f:
        f.write("Signature Truffle Pasta\n")
        f.write("Ingredients needed:\n")
        f.write("- Truffle Oil: 250 ml\n")
        f.write("- Parmesan: 350 grams\n")
        
    # Inventory
    inventory_data = [
        ["Ingredient", "Quantity", "Unit"],
        ["Saffron", "2", "grams"],
        ["Arborio Rice", "200", "grams"],
        ["Truffle Oil", "0", "ml"],
        ["Parmesan", "0", "grams"]
    ]
    with open(os.path.join(base_dir, "inventory.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)
        
    # Supplier Prices
    supplier_data = {
        "Saffron": [
            {"supplier": "Gourmet Co", "price_per_unit": 10.0, "unit": "grams"},
            {"supplier": "Spice Imports", "price_per_unit": 9.5, "unit": "grams"} # Cheapest
        ],
        "Arborio Rice": [
            {"supplier": "Gourmet Co", "price_per_unit": 6.0, "unit": "kg"},
            {"supplier": "Bulk Foods", "price_per_unit": 5.0, "unit": "kg"} # Cheapest
        ],
        "Truffle Oil": [
            {"supplier": "Luxury Liquids", "price_per_unit": 100.0, "unit": "liters"}, # Cheapest
            {"supplier": "Gourmet Co", "price_per_unit": 120.0, "unit": "liters"}
        ],
        "Parmesan": [
            {"supplier": "Dairy Farms", "price_per_unit": 20.0, "unit": "kg"}, # Cheapest
            {"supplier": "Bulk Foods", "price_per_unit": 22.0, "unit": "kg"}
        ]
    }
    with open(os.path.join(base_dir, "supplier_prices.json"), "w") as f:
        json.dump(supplier_data, f, indent=4)

if __name__ == "__main__":
    build_env()
