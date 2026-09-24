import os
import json
import re

def verify():
    state = {
        "report_file_exists": False,
        "is_valid_json": False,
        "misplaced_items_correct": False,
        "total_value_correct": False,
        "overtime_employees_correct": False
    }

    report_path = os.path.join("reports", "floor_audit.json")
    
    if os.path.exists(report_path):
        state["report_file_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True

            # Convert JSON to string to do robust searching, just in case they used weird keys
            data_str = json.dumps(data).lower()
            
            # 1. Check misplaced items (IDs: 102, 104, 106, 108)
            all_numbers = set(re.findall(r'\b10[2468]\b', data_str))
            if all_numbers == {'102', '104', '106', '108'}:
                # Ensure valid apparel items are NOT included
                apparel_ids = set(re.findall(r'\b10[13579]\b', data_str))
                if not apparel_ids:
                    state["misplaced_items_correct"] = True

            # 2. Check total value (15*5 + 12.50*4 + 20*2 + 30*1 = 195.00)
            if "195" in data_str or "195.0" in data_str or "195.00" in data_str:
                state["total_value_correct"] = True

            # 3. Check overtime employees (Mike, David, Tom)
            names_found = set()
            for name in ["mike", "david", "tom"]:
                if name in data_str:
                    names_found.add(name)
            
            # Ensure valid employees are NOT included
            valid_names_found = False
            for v_name in ["sarah", "jessica", "emily"]:
                if v_name in data_str:
                    valid_names_found = True
                    break
                    
            if len(names_found) == 3 and not valid_names_found:
                state["overtime_employees_correct"] = True

        except Exception:
            pass

    # Write objective state to physics probe
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
