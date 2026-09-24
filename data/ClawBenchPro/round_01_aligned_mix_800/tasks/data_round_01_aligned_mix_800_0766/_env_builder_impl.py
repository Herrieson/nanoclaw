import os
import json
import csv

os.makedirs("reports", exist_ok=True)

starting_stock = {
    "Saffron": {"qty": 10, "price": 15.0},
    "Bomba Rice": {"qty": 20, "price": 8.0},
    "Chorizo": {"qty": 15, "price": 12.0},
    "Manchego Cheese": {"qty": 5, "price": 20.0},
    "Smoked Paprika": {"qty": 8, "price": 6.0}
}
with open("starting_stock.json", "w", encoding="utf-8") as f:
    json.dump(starting_stock, f, indent=2)

sales_log = [
    {"tx_id": 1, "item": "Saffron", "price_charged": 15.0, "cashier": "Elena"},
    {"tx_id": 2, "item": "Bomba Rice", "price_charged": 8.0, "cashier": "Elena"},
    {"tx_id": 3, "item": "Chorizo", "price_charged": 10.0, "cashier": "Chad"}, 
    {"tx_id": 4, "item": "Saffron", "price_charged": 15.0, "cashier": "Chad"},
    {"tx_id": 5, "item": "Manchego Cheese", "price_charged": 15.0, "cashier": "Chad"}, 
    {"tx_id": 6, "item": "Bomba Rice", "price_charged": 8.0, "cashier": "Elena"},
    {"tx_id": 7, "item": "Smoked Paprika", "price_charged": 6.0, "cashier": "Elena"},
    {"tx_id": 8, "item": "Saffron", "price_charged": 15.0, "cashier": "Elena"},
    {"tx_id": 9, "item": "Saffron", "price_charged": 15.0, "cashier": "Chad"}
]
with open("sales_log.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["tx_id", "item", "price_charged", "cashier"])
    writer.writeheader()
    writer.writerows(sales_log)

paella_recipe = {
    "Saffron": 7, 
    "Bomba Rice": 2,
    "Chorizo": 1,
    "Smoked Paprika": 1
}
with open("paella_recipe.json", "w", encoding="utf-8") as f:
    json.dump(paella_recipe, f, indent=2)
