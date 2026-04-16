import os
import json
import csv

def verify():
    base_dir = "."
    orders_csv_path = os.path.join(base_dir, "urgent_orders.csv")
    
    state = {
        "csv_exists": False,
        "correct_headers": False,
        "no_duplicates": False,
        "correct_items_found": False,
        "correct_quantities": False,
        "all_data_correct": False,
        "error": None
    }

    if not os.path.exists(orders_csv_path):
        state["error"] = "urgent_orders.csv not found."
        print(json.dumps(state))
        return

    state["csv_exists"] = True

    expected_items = {
        "ITM-001": {"name": "Premium Saffron Threads", "email": "spices@gourmet-imports.com"},
        "ITM-003": {"name": "Jamón Ibérico de Bellota", "email": "meats@spain-foods.es"},
        "ITM-005": {"name": "Organic Bomba Rice", "email": "grains@paella-supplies.com"},
        "ITM-006": {"name": "Smoked Paprika (Pimentón)", "email": "spices@gourmet-imports.com"}
    }

    found_items = {}
    
    try:
        with open(orders_csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            
            if headers == ['ItemCode', 'ItemName', 'SupplierEmail', 'OrderQuantity']:
                state["correct_headers"] = True
            
            has_duplicates = False
            all_qty_50 = True
            
            for row in reader:
                if len(row) != 4:
                    continue
                code, name, email, qty = row
                
                if code in found_items:
                    has_duplicates = True
                
                found_items[code] = {
                    "name": name,
                    "email": email,
                    "qty": qty
                }
                
                if str(qty).strip() != "50":
                    all_qty_50 = False

            state["no_duplicates"] = not has_duplicates
            state["correct_quantities"] = all_qty_50

            # Check if exactly the expected items were found and details match
            if set(found_items.keys()) == set(expected_items.keys()):
                match = True
                for code, data in expected_items.items():
                    if found_items[code]["name"] != data["name"] or found_items[code]["email"] != data["email"]:
                        match = False
                state["correct_items_found"] = match

            if state["correct_headers"] and state["no_duplicates"] and state["correct_items_found"] and state["correct_quantities"]:
                state["all_data_correct"] = True

    except Exception as e:
        state["error"] = str(e)

    print(json.dumps(state))

if __name__ == "__main__":
    verify()
