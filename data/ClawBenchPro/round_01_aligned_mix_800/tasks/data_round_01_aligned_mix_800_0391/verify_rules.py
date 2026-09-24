import os
import json
import re

def verify():
    state = {
        "audit_file_exists": False,
        "is_valid_json": False,
        "total_cost_correct": False,
        "vips_correct": False,
        "no_false_positives": True
    }

    audit_path = os.path.join("desk", "audit.json")
    
    if os.path.exists(audit_path):
        state["audit_file_exists"] = True
        try:
            with open(audit_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            data_str = json.dumps(data).lower()
            
            # Expected Food & Beverage costs:
            # Food-Catering: 1050.50
            # Beverage-Wine: 320.25
            # Food-Appetizers: 89.99
            # Beverage-SparklingWater: 40.00
            # Total: 1500.74
            
            def check_val_recursively(obj, target):
                if isinstance(obj, dict):
                    return any(check_val_recursively(v, target) for v in obj.values())
                elif isinstance(obj, list):
                    return any(check_val_recursively(v, target) for v in obj)
                elif isinstance(obj, (int, float)):
                    return abs(obj - target) < 0.01
                elif isinstance(obj, str):
                    try:
                        return abs(float(re.sub(r'[^\d.]', '', obj)) - target) < 0.01
                    except:
                        return False
                return False

            if check_val_recursively(data, 1500.74) or ("1500.74" in data_str):
                state["total_cost_correct"] = True

            # Expected problematic VIPs (Those who return 'None' from the mock API): 
            # "Alice Walker", "Margaret Atwood", "Toni Morrison"
            expected_vips = ["alice walker", "margaret atwood", "toni morrison"]
            found_all = all(vip in data_str for vip in expected_vips)
            
            if found_all:
                state["vips_correct"] = True

            # False positives check
            false_positives = ["bob general", "han kang", "stephen king", "jane doe", "james baldwin"]
            if any(fp in data_str for fp in false_positives):
                state["no_false_positives"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
