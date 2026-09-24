import os
import json

def verify():
    state = {
        "summary_file_exists": False,
        "is_valid_json": False,
        "correct_revenue_found": False,
        "correct_expenses_found": False,
        "personal_expense_excluded": True
    }

    target_file = "accountant_ready/tax_headache_summary.json"

    if os.path.exists(target_file):
        state["summary_file_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
            
            state["is_valid_json"] = True
            
            # Convert JSON back to string to easily check if the exact numerical values exist in any field
            data_str = json.dumps(data)
            
            # Total Revenue should be 2500 + 800 + 1200 = 4500
            if "4500" in data_str or "4500.0" in data_str:
                state["correct_revenue_found"] = True
                
            # Total Expenses should be 400 + 150 + 85.50 + 45 + 120 + 30 = 830.50
            if "830.5" in data_str or "830.50" in data_str:
                state["correct_expenses_found"] = True

            # If they included the $15 personal bandana, the expense would be 845.50
            if "845.5" in data_str or "845.50" in data_str:
                state["personal_expense_excluded"] = False

        except Exception:
            # File exists but is not valid JSON or unreadable
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
