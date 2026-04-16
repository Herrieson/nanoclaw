import os
import json

def verify():
    result = {
        "has_manifest_file": False,
        "valid_json": False,
        "correct_order_count": False,
        "correct_data_mapping": False,
        "correct_price_calculation": False
    }
    
    manifest_path = "shipping_manifest.json"
    if not os.path.exists(manifest_path):
        # Check if it was placed inside workspace or current dir
        if os.path.exists("shipping_manifest.json"):
            manifest_path = "shipping_manifest.json"
        else:
            with open("verify_result.json", "w") as f:
                json.dump(result, f)
            return

    result["has_manifest_file"] = True
    
    try:
        with open(manifest_path, "r") as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception:
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    if isinstance(data, list) and len(data) == 4:
        result["correct_order_count"] = True
        
    # Expected Ground Truth
    expected_orders = {
        "978-0141439518": {
            "buyer_name": "Alice Wonderland",
            "address": "123 Rabbit Hole Ln, CT",
            "book_title": "Pride and Prejudice",
            "final_price": 21.68  # 25.50 * 0.85 = 21.675 -> 21.68
        },
        "978-0743273565": {
            "buyer_name": "Charlie Brown",
            "address": "789 Peanut St, MA",
            "book_title": "The Great Gatsby",
            "final_price": 25.50  # 30.00 * 0.85 = 25.50
        },
        "978-0544003415": {
            "buyer_name": "Diana Prince",
            "address": "1 Themyscira Ave, VA",
            "book_title": "The Lord of the Rings",
            "final_price": 55.25  # 65.00 * 0.85 = 55.25
        },
        "978-0439023481": {
            "buyer_name": "Evan Hansen",
            "address": "321 Broadway, NY",
            "book_title": "The Hunger Games",
            "final_price": 12.92  # 15.20 * 0.85 = 12.92
        }
    }
    
    mapping_correct = True
    price_correct = True
    
    if not isinstance(data, list):
        mapping_correct = False
        price_correct = False
    else:
        found_isbns = set()
        for item in data:
            isbn = item.get("isbn")
            if isbn not in expected_orders:
                mapping_correct = False
                continue
            
            found_isbns.add(isbn)
            exp = expected_orders[isbn]
            
            if item.get("buyer_name") != exp["buyer_name"] or \
               item.get("address") != exp["address"] or \
               item.get("book_title") != exp["book_title"]:
                mapping_correct = False
                
            # Allow minor float precision issues but strictly enforce rounding logic requirement loosely
            price = item.get("final_price")
            if not isinstance(price, (int, float)) or abs(price - exp["final_price"]) > 0.01:
                price_correct = False
                
        if len(found_isbns) != 4:
            mapping_correct = False

    result["correct_data_mapping"] = mapping_correct
    result["correct_price_calculation"] = price_correct
    
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
