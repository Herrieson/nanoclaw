import os
import json
import sys

def extract_pos_data(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File {file_path} not found."})
    
    # Simulate reading the binary dump and extracting records
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
    return json.dumps(sales_log)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(extract_pos_data(sys.argv[1]))
    else:
        print(json.dumps({"error": "Missing file_path parameter"}))
