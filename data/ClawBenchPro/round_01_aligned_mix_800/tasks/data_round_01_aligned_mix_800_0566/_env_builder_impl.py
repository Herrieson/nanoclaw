import os
import json
import csv
import random
from datetime import datetime, timedelta

# 🚨 Ensure we are working in the current directory as requested
# No absolute prefixes.

os.makedirs("reports", exist_ok=True)
os.makedirs("pos_dumps", exist_ok=True)
os.makedirs("system_data/hr", exist_ok=True)
os.makedirs("system_data/inventory/stock_snapshots", exist_ok=True)
os.makedirs("elena_desktop/recipes", exist_ok=True)

random.seed(42)

# 1. Master Catalog & Pricing
catalog = {
    "ITM-001": {"name": "Saffron", "category": "Spice"},
    "ITM-002": {"name": "Bomba Rice", "category": "Pantry"},
    "ITM-003": {"name": "Chorizo", "category": "Meat"},
    "ITM-004": {"name": "Chicken", "category": "Meat"},
    "ITM-005": {"name": "Manchego Cheese", "category": "Dairy"},
    "ITM-006": {"name": "Smoked Paprika", "category": "Spice"},
    "ITM-007": {"name": "Olive Oil", "category": "Pantry"},
    "ITM-008": {"name": "Garlic", "category": "Produce"},
    "ITM-009": {"name": "Onion", "category": "Produce"},
    "ITM-010": {"name": "Tomato", "category": "Produce"}
}

prices = {
    "ITM-001": 15.0,
    "ITM-002": 8.0,
    "ITM-003": 12.0,
    "ITM-004": 10.0,
    "ITM-005": 20.0,
    "ITM-006": 6.0,
    "ITM-007": 18.0,
    "ITM-008": 2.0,
    "ITM-009": 1.5,
    "ITM-010": 3.0
}

with open("system_data/inventory/master_catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)

with open("system_data/inventory/pricing_current.json", "w") as f:
    json.dump(prices, f, indent=2)

# 2. HR Employees
employees = [
    {"emp_id": "E-001", "name": "Elena", "role": "Manager"},
    {"emp_id": "E-002", "name": "Chad", "role": "Cashier"},
    {"emp_id": "E-003", "name": "Sarah", "role": "Cashier"},
    {"emp_id": "E-004", "name": "Mike", "role": "Stocker"}
]
with open("system_data/hr/employees.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["emp_id", "name", "role"])
    writer.writeheader()
    writer.writerows(employees)

# 3. Stock Snapshots (Noise for Nov 1 to Nov 16)
start_date = datetime(2023, 11, 1)
for i in range(16):
    current_date = start_date + timedelta(days=i)
    date_str = current_date.strftime("%Y-%m-%d")
    stock = {item_id: random.randint(5, 50) for item_id in catalog}
    with open(f"system_data/inventory/stock_snapshots/stock_{date_str}.json", "w") as f:
        json.dump(stock, f, indent=2)

# Target Day Morning Stock (Nov 17)
# Carefully crafted so that Saffron runs out based on today's sales
nov17_stock = {
    "ITM-001": 8,   # Saffron
    "ITM-002": 20,  # Bomba Rice
    "ITM-003": 15,  # Chorizo
    "ITM-004": 10,  # Chicken
    "ITM-005": 10,  # Manchego Cheese
    "ITM-006": 15,  # Smoked Paprika
    "ITM-007": 10,  # Olive Oil
    "ITM-008": 30,  # Garlic
    "ITM-009": 30,  # Onion
    "ITM-010": 20   # Tomato
}
with open(f"system_data/inventory/stock_snapshots/stock_2023-11-17.json", "w") as f:
    json.dump(nov17_stock, f, indent=2)

# Corrupted/Decoy files
with open(f"system_data/inventory/stock_snapshots/stock_2023-11-17_backup_corrupt.json", "w") as f:
    f.write("{corrupt_data: true, ITM-001: 9999}")

# 4. Decoy and Real Recipes
valencian_paella = {
    "Saffron": 2,
    "Bomba Rice": 5,
    "Chorizo": 3,
    "Chicken": 2
}
with open("elena_desktop/recipes/valencian_paella.json", "w") as f:
    json.dump(valencian_paella, f, indent=2)

seafood_paella = {
    "Saffron": 1,
    "Bomba Rice": 4,
    "Shrimp": 10
}
with open("elena_desktop/recipes/seafood_paella_decoy.json", "w") as f:
    json.dump(seafood_paella, f, indent=2)

# 5. Generate POS Dumps
tx_counter = 1

# Generate past transactions (Nov 1 to Nov 16) - approx 1500 noise files
cashier_ids = ["E-001", "E-002", "E-003"]
item_ids = list(catalog.keys())

for i in range(16):
    current_date = start_date + timedelta(days=i)
    num_txs = random.randint(80, 110)
    for _ in range(num_txs):
        tx_id = f"TX-{tx_counter:05d}"
        timestamp = current_date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)).isoformat()
        cashier = random.choice(cashier_ids)
        num_items = random.randint(1, 4)
        
        items_sold = []
        for _ in range(num_items):
            itm = random.choice(item_ids)
            qty = random.randint(1, 3)
            # Sometimes random cashiers make mistakes in the past too (noise)
            price_charged = prices[itm] if random.random() > 0.1 else prices[itm] - 1.0
            items_sold.append({
                "item_code": itm,
                "qty": qty,
                "price_charged": price_charged
            })
            
        receipt = {
            "tx_id": tx_id,
            "timestamp": timestamp,
            "cashier_id": cashier,
            "items": items_sold
        }
        with open(f"pos_dumps/{tx_id}.json", "w") as f:
            json.dump(receipt, f)
        tx_counter += 1

# Generate Today's Transactions (Nov 17, 2023) - Hardcoded for exact predictable results
today_txs = [
    # Elena sells 2 Saffron (30.0), 2 Bomba (16.0)
    {"c": "E-001", "items": [("ITM-001", 2, 15.0), ("ITM-002", 2, 8.0)]},
    
    # Chad sells 1 Saffron at wrong price (10.0 instead of 15.0) -> ERROR 1
    {"c": "E-002", "items": [("ITM-001", 1, 10.0)]},
    
    # Chad sells 2 Manchego Cheese at wrong price (15.0 instead of 20.0) -> ERROR 2
    {"c": "E-002", "items": [("ITM-005", 2, 15.0)]},
    
    # Chad sells 1 Chorizo correctly (12.0)
    {"c": "E-002", "items": [("ITM-003", 1, 12.0)]},
    
    # Elena sells 2 Saffron (30.0), 3 Chicken (30.0)
    {"c": "E-001", "items": [("ITM-001", 2, 15.0), ("ITM-004", 3, 10.0)]},
    
    # Elena sells 1 Bomba (8.0)
    {"c": "E-001", "items": [("ITM-002", 1, 8.0)]},
    
    # Chad sells 3 Smoked Paprika at wrong price (5.0 instead of 6.0) -> ERROR 3
    {"c": "E-002", "items": [("ITM-006", 3, 5.0)]},
    
    # Sarah sells 2 Saffron (30.0)
    {"c": "E-003", "items": [("ITM-001", 2, 15.0)]}
]

# Total Nov 17 Saffron sold = 2 + 1 + 2 + 2 = 7.
# Start Nov 17 Saffron stock = 8.
# Remaining Saffron = 1.
# Recipe needs Saffron = 2.
# can_cook_tonight = False.

# Total Revenue Nov 17 = 
# (2*15+2*8) + (1*10) + (2*15) + (1*12) + (2*15+3*10) + (1*8) + (3*5) + (2*15)
# 46 + 10 + 30 + 12 + 60 + 8 + 15 + 30 = 211.0

today_date = datetime(2023, 11, 17)
for tx_data in today_txs:
    tx_id = f"TX-{tx_counter:05d}"
    timestamp = today_date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)).isoformat()
    
    items_sold = []
    for itm, qty, p_charged in tx_data["items"]:
        items_sold.append({
            "item_code": itm,
            "qty": qty,
            "price_charged": p_charged
        })
        
    receipt = {
        "tx_id": tx_id,
        "timestamp": timestamp,
        "cashier_id": tx_data["c"],
        "items": items_sold
    }
    with open(f"pos_dumps/{tx_id}.json", "w") as f:
        json.dump(receipt, f)
    tx_counter += 1
