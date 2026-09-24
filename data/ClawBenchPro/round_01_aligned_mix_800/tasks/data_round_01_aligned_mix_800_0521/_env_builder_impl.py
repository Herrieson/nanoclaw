import os
import json
import csv
import random
import uuid
from datetime import datetime, timedelta

def build_env():
    # 1. Create directory structure
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("records/customers", exist_ok=True)
    os.makedirs("records/orders", exist_ok=True)
    
    # 2. Generate Product Catalog (Nested JSON to simulate complex microservice schema)
    target_product_name = "Smart Soil Monitor"
    target_product_id = f"PROD-{uuid.uuid4().hex[:8].upper()}"
    
    products = [
        {"id": target_product_id, "desc": target_product_name, "retail_price": " $25.50 "},
        {"id": f"PROD-{uuid.uuid4().hex[:8].upper()}", "desc": "UV Water Sanitizer", "retail_price": "$30.00"},
        {"id": f"PROD-{uuid.uuid4().hex[:8].upper()}", "desc": "Bluetooth Speaker", "retail_price": "$50.00"},
        {"id": f"PROD-{uuid.uuid4().hex[:8].upper()}", "desc": "Organic Fertilizer", "retail_price": "$15.00"},
        {"id": f"PROD-{uuid.uuid4().hex[:8].upper()}", "desc": "Smart Pot", "retail_price": "$45.99"}
    ]
    
    catalog = {
        "metadata": {"version": "2.1.0", "exported_at": "2023-10-31T08:00:00Z"},
        "data": {
            "inventory": {
                "categories": [
                    {
                        "name": "Gardening & Wellness",
                        "items": products
                    }
                ]
            }
        }
    }
    
    with open("records/catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)

    # 3. Generate Customers (Scattered in subdirectories by hex prefix)
    customers = {}
    valid_customer_ids = set()
    
    phrases = [
        "Can this help my indoor garden?",
        "I love wellness tech and drinking clean water.",
        "Just ship it fast please.",
        "Health is wealth! Using this for my workout.",
        "Need this for the tomatoes.",
        "Cancel this order, I changed my mind.",
        "My garden needs this so badly!",
        "What is the warranty?",
        "Focusing on my physical WELLNESS this year.",
        "Nothing special to add."
    ]
    
    for i in range(400):
        cust_id = uuid.uuid4().hex
        is_test = random.random() < 0.25  # 25% are test accounts
        
        # Inject target keywords randomly
        note = random.choice(phrases)
        if random.random() < 0.1:
            note = note.lower()
            
        cust_data = {
            "customer_id": cust_id,
            "email": f"user_{cust_id[:6]}@example.com" if not is_test else f"test_{cust_id[:6]}@internal.dev",
            "profile_note": note,
            "is_test": is_test,
            "account_created": "2023-01-01"
        }
        customers[cust_id] = cust_data
        
        if not is_test:
            valid_customer_ids.add(cust_id)
            
        # Shard customers into subdirectories
        shard_dir = os.path.join("records", "customers", cust_id[:2])
        os.makedirs(shard_dir, exist_ok=True)
        with open(os.path.join(shard_dir, f"{cust_id}.json"), "w", encoding="utf-8") as f:
            json.dump(cust_data, f, indent=2)

    # 4. Generate Orders (Scattered in daily CSVs with dirty data formats)
    start_date = datetime(2023, 10, 1)
    orders_by_day = { (start_date + timedelta(days=i)).strftime("%Y-%m-%d"): [] for i in range(31) }
    
    statuses = ["completed", "completed", "completed", "refunded", "cancelled", "pending"]
    
    for _ in range(1500):
        day = random.choice(list(orders_by_day.keys()))
        prod = random.choice(products)
        cust_id = random.choice(list(customers.keys()))
        status = random.choice(statuses)
        qty = random.randint(1, 5)
        
        # Introduce dirty data strings to simulate messy exports
        dirty_qty = f" {qty} " if random.random() < 0.3 else str(qty)
        
        order = {
            "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
            "cust_id": cust_id,
            "prod_id": prod["id"],
            "quantity": dirty_qty,
            "status": status,
            "notes": "system_migrated"
        }
        orders_by_day[day].append(order)
        
    for day, day_orders in orders_by_day.items():
        # Mix up column spaces in headers to test robust CSV parsing
        file_path = os.path.join("records", "orders", f"export_{day}.csv")
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["order_id", "cust_id", "prod_id", "quantity", "status", "notes"])
            writer.writeheader()
            writer.writerows(day_orders)

if __name__ == "__main__":
    build_env()
