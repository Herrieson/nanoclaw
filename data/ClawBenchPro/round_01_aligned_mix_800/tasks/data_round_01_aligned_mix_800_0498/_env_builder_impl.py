import os
import csv
import json
import random

def build_env():
    # Set a fixed seed for deterministic wasteland generation
    random.seed(42)

    os.makedirs("procurement", exist_ok=True)
    os.makedirs("quotes", exist_ok=True)
    os.makedirs("financial_forecast", exist_ok=True)

    # 1. Create rules.json in procurement
    rules = {
        "exchange_rates": {
            "USD": 1.0,
            "EUR": 1.10,
            "GBP": 1.25,
            "JPY": 0.01
        },
        "premium_tags": ["imported", "rare", "organic", "exclusive", "premium"],
        "premium_fee_multiplier": 1.20
    }
    with open("procurement/rules.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=4)

    # 2. Setup the vendor registry and vendor directories
    vendors = []
    statuses = ["APPROVED", "REJECTED", "PENDING", "BLACKLISTED"]
    
    ingredients = [
        "Lobster", "Oysters", "Chardonnay", "Pinot Noir", "Truffles", 
        "Wagyu Beef", "Caviar", "Saffron", "Heirloom Tomatoes", "Artisan Cheese",
        "Balsamic Vinegar", "Iberico Ham", "Matcha Powder", "Vanilla Beans", "King Crab"
    ]
    all_tags = ["local", "imported", "farm-raised", "wild-caught", "rare", "organic", "standard", "exclusive", "bulk", "premium"]
    currencies = ["USD", "EUR", "GBP", "JPY"]

    # Generate 150 vendors for scale and noise
    for i in range(1, 151):
        vendor_id = f"vendor_{i:03d}"
        vendor_name = f"Vendor_Corp_{i}"
        
        # Make roughly 20% of vendors APPROVED
        status = "APPROVED" if random.random() < 0.2 else random.choice(statuses[1:])
        vendors.append([vendor_id, vendor_name, status])
        
        vendor_dir = os.path.join("quotes", vendor_id)
        os.makedirs(vendor_dir, exist_ok=True)
        
        # Create noise files for every vendor
        for draft_num in range(1, random.randint(3, 7)):
            with open(os.path.join(vendor_dir, f"draft_v{draft_num}.json"), "w", encoding="utf-8") as f:
                json.dump({"status": "draft", "warning": "DO NOT USE"}, f)
        
        with open(os.path.join(vendor_dir, "internal_notes.txt"), "w", encoding="utf-8") as f:
            f.write("Need to revise pricing based on last week's email.\n")

        # If approved, generate the exact one valid 'final_quote' file
        if status == "APPROVED":
            file_type = random.choice(["json", "csv"])
            file_name = f"final_quote_{random.randint(1000, 9999)}.{file_type}"
            file_path = os.path.join(vendor_dir, file_name)
            
            num_items = random.randint(1, 4)
            items_data = []
            
            for _ in range(num_items):
                base_price = random.randint(10, 200) * 10
                # Generate a mix of spiked (>15%) and normal items
                if random.random() < 0.4:
                    current_price = int(base_price * random.uniform(1.16, 1.50))
                else:
                    current_price = int(base_price * random.uniform(0.9, 1.10))
                
                item = {
                    "item_name": f"{random.choice(ingredients)} {random.randint(1, 100)}",
                    "base_price": base_price,
                    "current_price": current_price,
                    "currency": random.choice(currencies),
                    "tags": random.sample(all_tags, random.randint(1, 3))
                }
                items_data.append(item)
            
            if file_type == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(items_data, f, indent=4)
            else:
                with open(file_path, "w", encoding="utf-8", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["item_name", "base_price", "current_price", "currency", "tags"])
                    for item in items_data:
                        tags_str = "|".join(item["tags"])
                        writer.writerow([
                            item["item_name"], 
                            item["base_price"], 
                            item["current_price"], 
                            item["currency"], 
                            tags_str
                        ])

    # Write the vendor registry
    with open("procurement/vendor_registry.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["vendor_id", "vendor_name", "status"])
        writer.writerows(vendors)

if __name__ == "__main__":
    build_env()
