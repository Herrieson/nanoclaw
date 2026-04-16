import os
import json

def verify():
    target_file = "q3_commission_summary.json"
    state = {
        "file_exists": False,
        "valid_json": False,
        "correct_beryllium": False,
        "correct_titanium": False,
        "correct_commission": False,
        "actual_data": None
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            state["valid_json"] = True
            state["actual_data"] = data

            # Expected values based on env_builder
            # Beryllium: 45000 + 32000 = 77000
            # Titanium: 120500 + 88000 = 208500
            # Total Sales: 285500
            # Commission (5%): 14275
            
            if data.get("Beryllium_sales") == 77000:
                state["correct_beryllium"] = True
            
            if data.get("Titanium_sales") == 208500:
                state["correct_titanium"] = True
            
            # Allow float or int
            if data.get("total_commission") in [14275, 14275.0]:
                state["correct_commission"] = True
                
        except Exception as e:
            pass

    with open("verify_result.json", "w", encoding='utf-8') as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
