import os
import json
import csv
import random

def build_env():
    # 1. Create Directories
    os.makedirs("bank_dump", exist_ok=True)
    os.makedirs("family_recipes", exist_ok=True)
    os.makedirs("store_catalogs", exist_ok=True)
    os.makedirs("cookout_plan", exist_ok=True)

    random.seed(42)

    # 2. Generate Bank Transactions (Scale & Noise)
    # We strictly need October CLEARED INCOME to be 4500, EXPENSE to be 3300. (Leftover = 1200, Budget = 120)
    with open("bank_dump/transactions.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "date", "amount", "type", "status", "description"])
        tx_id = 1000
        
        # Target October CLEARED
        for _ in range(3):
            writer.writerow([tx_id, "2023-10-15", 1500.00, "INCOME", "CLEARED", "Payroll"])
            tx_id += 1
            
        for _ in range(33):
            writer.writerow([tx_id, "2023-10-20", 100.00, "EXPENSE", "CLEARED", "Bill"])
            tx_id += 1
            
        # Massive Noise Generator
        for month in ["08", "09", "10", "11", "12"]:
            for _ in range(250):
                status = random.choice(["CLEARED", "PENDING", "FAILED"])
                ttype = random.choice(["INCOME", "EXPENSE"])
                amt = round(random.uniform(5.0, 500.0), 2)
                
                # Make sure we don't accidentally add valid CLEARED transactions to October
                if month == "10" and status == "CLEARED":
                    status = random.choice(["PENDING", "FAILED"])
                    
                date_day = str(random.randint(1, 28)).zfill(2)
                writer.writerow([tx_id, f"2023-{month}-{date_day}", amt, ttype, status, "Misc Transaction"])
                tx_id += 1

    # 3. Generate Recipes (Fragmentation & Decoys)
    # 50 folders, 20 files each = 1000 files. Only one is correct.
    target_folder = random.randint(0, 49)
    target_file = random.randint(0, 19)

    for i in range(50):
        folder_path = f"family_recipes/box_{i}"
        os.makedirs(folder_path, exist_ok=True)
        for j in range(20):
            file_path = f"{folder_path}/recipe_{j}.json"
            if i == target_folder and j == target_file:
                recipe = {
                    "dish_name": "Birria Tradicional",
                    "author": "Abuela Maria",
                    "servings": 5,
                    "ingredients": {
                        "beef_chuck_lbs": 3,
                        "dried_guajillo_chiles": 6,
                        "garlic_cloves": 4,
                        "onion": 1,
                        "corn_tortillas_pack": 1
                    },
                    "secret_note": "Do not skip the chiles!"
                }
            else:
                # Decoys
                dish_names = ["Birria Falsa", "Tacos de Perro", "Enchiladas", "Birria Tradicional", "Sopa"]
                authors = ["Abuela Maria", "Tio Juan", "Cousin Luis", "Fake Author"]
                
                dish = random.choice(dish_names)
                author = random.choice(authors)
                
                # Ensure no accidental exact match
                if dish == "Birria Tradicional" and author == "Abuela Maria":
                    author = "Tio Juan"
                    
                recipe = {
                    "dish_name": dish,
                    "author": author,
                    "servings": random.randint(2, 10),
                    "ingredients": {
                        f"random_ingredient_{random.randint(1,100)}": random.randint(1, 5)
                    }
                }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(recipe, f, indent=4)

    # 4. Generate Store Catalogs (Multi-hop & Noise)
    stores = ["Supermercado La Fiesta", "El Mercado del Barrio", "Walmart", "Target", "Costco"]
    items = ["beef_chuck_lbs", "dried_guajillo_chiles", "garlic_cloves", "onion", "corn_tortillas_pack", "cerveza_six_pack", "limes_lb", "tomato", "cilantro", "avocado"]

    with open("store_catalogs/national_prices.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["store_name", "item_name", "price"])
        
        # Real prices for target store
        fiesta_prices = {
            "beef_chuck_lbs": 6.50,
            "dried_guajillo_chiles": 0.20,
            "garlic_cloves": 0.10,
            "onion": 0.80,
            "corn_tortillas_pack": 3.00,
            "cerveza_six_pack": 8.99,
            "limes_lb": 1.50,
            "tomato": 0.50,
            "cilantro": 0.30,
            "avocado": 1.20
        }
        
        # Scramble writing order
        rows = []
        for store in stores:
            for item in items:
                if store == "Supermercado La Fiesta":
                    rows.append([store, item, fiesta_prices[item]])
                else:
                    # Random noisy prices
                    rows.append([store, item, round(random.uniform(0.1, 15.0), 2)])
                    
        random.shuffle(rows)
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    build_env()
