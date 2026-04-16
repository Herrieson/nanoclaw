import os
import json

def verify():
    base_dir = "."
    order_file = os.path.join(base_dir, "order.json")
    
    result = {
        "order_file_exists": False,
        "is_valid_json": False,
        "correct_quail_qty": False,
        "correct_dogfood_qty": False,
        "no_foxkibble_ordered": False,
        "exact_match": False,
        "error": None
    }
    
    if not os.path.exists(order_file):
        result["error"] = "order.json not found."
        return result
        
    result["order_file_exists"] = True
    
    try:
        with open(order_file, 'r') as f:
            data = json.load(f)
            result["is_valid_json"] = True
            
            # Expected logic:
            # Quail: needs 15, has 5 -> order 10
            # FoxKibble: needs 5, has 10 -> order 0 (should not be in dict or should be 0)
            # DogFood: needs 14, has 2 -> order 12
            
            quail = data.get("Quail", 0)
            dogfood = data.get("DogFood", 0)
            foxkibble = data.get("FoxKibble", 0)
            
            if quail == 10:
                result["correct_quail_qty"] = True
            if dogfood == 12:
                result["correct_dogfood_qty"] = True
            if foxkibble == 0:
                result["no_foxkibble_ordered"] = True
                
            # Check for exact strict match (ignoring keys with 0)
            cleaned_data = {k: v for k, v in data.items() if v > 0}
            expected_data = {"Quail": 10, "DogFood": 12}
            
            if cleaned_data == expected_data:
                result["exact_match"] = True
                
    except Exception as e:
        result["error"] = str(e)
        
    # Write structural state to verify_result.json
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
