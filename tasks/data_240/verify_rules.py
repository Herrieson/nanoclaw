import os
import csv
import json

def verify():
    # Ground truth calculations:
    # --- SF-001 (Dune, Warehouse: 15) ---
    # Store_A: 10 - 3 = 7. Needs 13.
    # Store_B: 12 - 4 = 8. Needs 12.
    # Store_C: 8 - 5 = 3. Needs 17.
    # Allocation order (Alpha -> Beta -> Gamma):
    # Alpha gets 13 (Warehouse left: 2)
    # Beta gets 2 (Warehouse left: 0)
    # Gamma gets 0
    #
    # --- FN-002 (Hobbit, Warehouse: 100) ---
    # Store_A: 15 - 0 = 15. Needs 5.
    # Store_B: 18 - 3 = 15. Needs 5.
    # Store_C: 20 - 0 = 20. Needs 0.
    # Allocation: Alpha: 5, Beta: 5
    #
    # --- SF-003 (Foundation, Warehouse: 8) ---
    # Store_A: 5 - 4 = 1. Needs 19.
    # Store_B: 6 - 2 = 4. Needs 16.
    # Store_C: 2 - 0 = 2. Needs 18.
    # Allocation: Alpha gets 8 (Warehouse left: 0). Beta: 0, Gamma: 0
    #
    # --- FN-005 (Mistborn, Warehouse: 50) ---
    # Store_A: 18 - 0 = 18. Needs 2.
    # Store_B: 20 - 0 = 20. Needs 0.
    # Store_C: 10 - 5 = 5. Needs 15.
    # Allocation: Alpha: 2, Gamma: 15
    
    expected_orders = {
        ("Store_A_Alpha", "SF-001"): 13,
        ("Store_B_Beta", "SF-001"): 2,
        ("Store_A_Alpha", "FN-002"): 5,
        ("Store_B_Beta", "FN-002"): 5,
        ("Store_A_Alpha", "SF-003"): 8,
        ("Store_A_Alpha", "FN-005"): 2,
        ("Store_C_Gamma", "FN-005"): 15
    }

    req_file = "requisitions.csv"
    result = {
        "file_exists": False,
        "valid_headers": False,
        "no_cooking_books": True,
        "correct_orders": 0,
        "total_expected_orders": len(expected_orders),
        "extra_orders": 0,
        "score": 0
    }

    if os.path.exists(req_file):
        result["file_exists"] = True
        try:
            with open(req_file, "r") as f:
                reader = csv.reader(f)
                headers = next(reader)
                if headers == ["StoreID", "SKU", "Title", "OrderQty"]:
                    result["valid_headers"] = True
                
                parsed_orders = {}
                for row in reader:
                    if len(row) != 4: continue
                    store, sku, title, qty = row
                    if "CK-" in sku:
                        result["no_cooking_books"] = False
                    
                    if int(qty) > 0:
                        parsed_orders[(store, sku)] = int(qty)
                
                correct_count = 0
                for k, v in expected_orders.items():
                    if parsed_orders.get(k) == v:
                        correct_count += 1
                
                result["correct_orders"] = correct_count
                
                # Check for any unexpected orders
                for k in parsed_orders:
                    if k not in expected_orders or parsed_orders[k] != expected_orders[k]:
                        result["extra_orders"] += 1

                # Calculate score
                score = 0
                if result["valid_headers"]: score += 10
                if result["no_cooking_books"]: score += 10
                
                order_score = (correct_count / len(expected_orders)) * 80
                penalty = result["extra_orders"] * 5
                
                result["score"] = max(0, min(100, int(score + order_score - penalty)))

        except Exception as e:
            result["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
