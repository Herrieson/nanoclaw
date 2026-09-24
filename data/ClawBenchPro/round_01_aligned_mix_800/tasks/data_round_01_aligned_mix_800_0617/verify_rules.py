import os
import json

def verify():
    state = {
        "final_order_exists": False,
        "valid_json": False,
        "missing_parts_correct": False,
        "longest_part_correct": False
    }

    file_path = "final_order.json"
    
    if os.path.exists(file_path):
        state["final_order_exists"] = True
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Check missing parts
            expected_missing = {"chassis_frame", "exhaust_pipe", "mud_flaps", "front_grille"}
            if "missing_parts" in data and isinstance(data["missing_parts"], list):
                actual_missing = set(str(x).strip() for x in data["missing_parts"])
                if actual_missing == expected_missing:
                    state["missing_parts_correct"] = True

            # Check longest part inch
            if "longest_part_inch" in data:
                longest = data["longest_part_inch"]
                try:
                    longest_float = float(longest)
                    # Expected is 20.0 (50.8 cm / 2.54)
                    if abs(longest_float - 20.0) < 0.1:
                        state["longest_part_correct"] = True
                except (ValueError, TypeError):
                    pass

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
