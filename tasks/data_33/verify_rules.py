import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "villa_nova_summary.json")
    
    state = {
        "file_exists": False,
        "valid_json": False,
        "correct_material_cost": False,
        "correct_permit_number": False,
        "extracted_cost": None,
        "extracted_permit": None
    }
    
    expected_cost = 1500.50 + 345.25 + 120.00 + 400.25 # 2366.00
    expected_permit = "VN-2023-8894"
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Check cost
            cost = data.get("total_material_cost")
            state["extracted_cost"] = cost
            if cost is not None:
                try:
                    if abs(float(cost) - expected_cost) < 0.01:
                        state["correct_material_cost"] = True
                except ValueError:
                    pass
            
            # Check permit
            permit = data.get("permit_number")
            state["extracted_permit"] = permit
            if permit == expected_permit:
                state["correct_permit_number"] = True
                
        except Exception as e:
            pass
            
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
