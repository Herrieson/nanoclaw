import os
import json
import csv

def build_env():
    # Create required directories
    os.makedirs("notes", exist_ok=True)
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("store", exist_ok=True)
    os.makedirs("cookout_plan", exist_ok=True)

    # 1. Finances Notes
    finances_content = """Hey, just tracking my monthly budget here:
Monthly Take-home Pay: $4000
Rent: $1200
Truck Payment: $450
Insurance: $200
Groceries (Personal): $300
Ah, and I almost forgot, I owe my cousin $150, but I'll pay him next month so don't include it in this month's bills.
"""
    with open("notes/finances.txt", "w", encoding="utf-8") as f:
        f.write(finances_content)

    # 2. Recipe Data
    recipe = {
        "name": "Abuela's Birria",
        "servings": 5,
        "ingredients": {
            "beef_chuck_lbs": 3,
            "dried_guajillo_chiles": 6,
            "garlic_cloves": 4,
            "onion": 1,
            "corn_tortillas_pack": 1
        }
    }
    with open("recipes/birria.json", "w", encoding="utf-8") as f:
        json.dump(recipe, f, indent=4)

    # 3. Store Prices
    with open("store/supermercado_prices.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "price_per_unit"])
        writer.writerow(["beef_chuck_lbs", 6.50])
        writer.writerow(["dried_guajillo_chiles", 0.20])
        writer.writerow(["garlic_cloves", 0.10])
        writer.writerow(["onion", 0.80])
        writer.writerow(["corn_tortillas_pack", 3.00])
        writer.writerow(["cerveza_six_pack", 8.99])  # distractor
        writer.writerow(["limes_lb", 1.50])          # distractor

if __name__ == "__main__":
    build_env()
