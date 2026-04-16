import os
import json

def verify():
    base_dir = "."
    inventory_path = os.path.join(base_dir, "inventory.json")
    missing_path = os.path.join(base_dir, "missing_item.txt")
    
    result = {
        "inventory_exists": False,
        "inventory_valid": False,
        "missing_item_exists": False,
        "missing_item_correct": False
    }
    
    # Check if inventory.json exists and is valid JSON containing all 5 items
    if os.path.exists(inventory_path):
        result["inventory_exists"] = True
        try:
            with open(inventory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) == 5:
                    result["inventory_valid"] = True
                elif isinstance(data, dict) and len(data.keys()) == 5:
                    result["inventory_valid"] = True
        except Exception:
            pass
            
    # Check if missing_item.txt exists and contains the correct item
    if os.path.exists(missing_path):
        result["missing_item_exists"] = True
        try:
            with open(missing_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                # The missing item is 104: 1890 Guard Whistle
                if "1890 guard whistle" in content or "guard whistle" in content or "104" in content:
                    result["missing_item_correct"] = True
        except Exception:
            pass
                
    # Output the result
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
