import os
import random
import json
import csv

def build_env():
    # Setup directories
    os.makedirs('supplier_drops', exist_ok=True)
    os.makedirs('design_notes', exist_ok=True)
    
    # --- 1. Generate Design Notes (Needle in a haystack) ---
    for i in range(1, 45):
        with open(f'design_notes/idea_draft_{i}.txt', 'w', encoding='utf-8') as f:
            f.write("Just some random bead thoughts...\nMaybe use more red?\n")
            
    with open('design_notes/salish_sea_amulet_v2_draft.txt', 'w', encoding='utf-8') as f:
        f.write("Materials list (DRAFT - DO NOT USE):\nM_8472 : 99\nM_9001 : 5\n")
        
    final_recipe_content = """Project: Salish Sea Amulet
Vibe: PNW Native progressive
Status: APPROVED

Materials list:
M_8472 : 5
M_1192 : 2
M_3310 : 10
M_9001 : 1

Notes: String them tightly.
"""
    with open('design_notes/salish_sea_amulet_v5_final.txt', 'w', encoding='utf-8') as f:
        f.write(final_recipe_content)

    # --- 2. Generate Messy Supplier Data ---
    # We will scatter valid and invalid items across multiple folders and formats.
    # We need to guarantee the prices for the target recipe to ensure deterministic output.
    # Target Target logic:
    # M_8472: Valid prices -> 4.50, 4.80. Out of stock -> 4.00. Fake supplier -> 2.00. (Cheapest valid: 4.50)
    # M_1192: Valid prices -> 1.20, 1.50. (Cheapest valid: 1.20)
    # M_3310: Valid prices -> 0.75, 0.80. (Cheapest valid: 0.75)
    # M_9001: Valid prices -> 15.00, 20.00. (Cheapest valid: 15.00)
    # Total cost = (5*4.50) + (2*1.20) + (10*0.75) + (1*15.00) = 22.5 + 2.4 + 7.5 + 15.0 = 47.40
    
    special_items = [
        {"id": "M_8472", "name": "Kingman Turquoise", "price_raw": " $ 4.50 ", "status": "In Stock", "auth": True},
        {"id": "M_8472", "name": "Kingman Turquoise", "price_raw": "4.80 USD", "status": "In Stock", "auth": True},
        {"id": "M_8472", "name": "Kingman Turquoise", "price_raw": "4.00", "status": "Out of Stock", "auth": True},
        {"id": "M_8472", "name": "Kingman Turquoise", "price_raw": "2.00 bucks", "status": "In Stock", "auth": False},
        
        {"id": "M_1192", "name": "Sterling Silver Spacer", "price_raw": "1.20", "status": " In Stock ", "auth": True},
        {"id": "M_1192", "name": "Sterling Silver Spacer", "price_raw": "approx 1.50", "status": "In Stock", "auth": True},
        
        {"id": "M_3310", "name": "Red Coral", "price_raw": "0.75 CAD", "status": "In Stock", "auth": True},
        {"id": "M_3310", "name": "Red Coral", "price_raw": "0.80", "status": "In Stock", "auth": True},
        
        {"id": "M_9001", "name": "Cedar Pendant", "price_raw": "$15.00", "status": "IN STOCK", "auth": True},
        {"id": "M_9001", "name": "Cedar Pendant", "price_raw": "20.00", "status": "In Stock", "auth": True},
    ]

    # Generate 500 random background items
    def random_price():
        val = round(random.uniform(0.1, 50.0), 2)
        formats = [f"${val}", f"{val} USD", f"approx {val}", f" {val} ", f"{val} bucks"]
        return random.choice(formats)
    
    def random_status():
        return random.choice(["In Stock", "Out of Stock", "Discontinued", "IN STOCK", " In Stock "])

    all_items = special_items[:]
    for i in range(500):
        all_items.append({
            "id": f"M_{random.randint(1000, 9999)}",
            "name": f"Random Bead {i}",
            "price_raw": random_price(),
            "status": random_status(),
            "auth": random.choice([True, True, False])
        })
        
    random.shuffle(all_items)
    
    # Distribute into 20 folders, each with multiple files
    for batch_num in range(1, 21):
        batch_dir = f"supplier_drops/batch_{202300 + batch_num}"
        os.makedirs(batch_dir, exist_ok=True)
        
        # Split items for this batch
        batch_items = [all_items.pop() for _ in range(len(all_items)) if random.random() < 0.1]
        if not all_items and batch_num == 20:
            batch_items = all_items # catch any remaining
            
        chunks = [batch_items[i:i + 15] for i in range(0, len(batch_items), 15)]
        
        for idx, chunk in enumerate(chunks):
            if not chunk: continue
            
            is_auth_file = chunk[0]['auth'] # Let the first item dictate the file's auth status roughly
            file_type = random.choice(['csv', 'tsv', 'json'])
            file_path = f"{batch_dir}/drop_{idx}.{file_type}"
            
            if file_type == 'json':
                data = {"items": []}
                if is_auth_file:
                    data["signature"] = "AUTHENTIC_SUPPLIER"
                for item in chunk:
                    data["items"].append({
                        "id": item["id"],
                        "name": item["name"],
                        "price": item["price_raw"],
                        "status": item["status"]
                    })
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    
            elif file_type == 'csv':
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    if is_auth_file:
                        writer.writerow(["# SIGNATURE: AUTHENTIC_SUPPLIER"])
                    writer.writerow(["# some random system comment"])
                    writer.writerow(["ID", "Name", "Price", "Status"])
                    for item in chunk:
                        writer.writerow([item["id"], item["name"], item["price_raw"], item["status"]])
                        
            elif file_type == 'tsv':
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f, delimiter='\t')
                    if is_auth_file:
                        writer.writerow(["# SIGNATURE: AUTHENTIC_SUPPLIER"])
                    writer.writerow(["ID", "Name", "Price", "Status"])
                    for item in chunk:
                        writer.writerow([item["id"], item["name"], item["price_raw"], item["status"]])

    # Catch any remaining items that didn't get popped
    if all_items:
        file_path = "supplier_drops/batch_202399_overflow/drop_final.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = {"signature": "AUTHENTIC_SUPPLIER", "items": []}
        for item in all_items:
            # force auth to match the file
            data["items"].append({
                "id": item["id"], "name": item["name"], "price": item["price_raw"], "status": item["status"]
            })
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

if __name__ == '__main__':
    build_env()
