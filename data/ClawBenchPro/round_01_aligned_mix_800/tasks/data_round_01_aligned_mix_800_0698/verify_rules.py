import os
import json
import math

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "has_total_cost": False,
        "total_cost_correct": False,
        "has_flagged_items": False,
        "flagged_items_correct": False
    }

    report_path = "financial_forecast/dinner_budget.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Look for cost
            cost_val = None
            for k, v in data.items():
                if isinstance(v, (int, float)):
                    cost_val = float(v)
                    state["has_total_cost"] = True
            
            if cost_val is not None:
                # 144.0 + 52.0 + 125.4 + 125.0 = 446.4
                if math.isclose(cost_val, 446.4, rel_tol=1e-3):
                    state["total_cost_correct"] = True
            
            # Look for items
            items_list = None
            for k, v in data.items():
                if isinstance(v, list):
                    items_list = v
                    state["has_flagged_items"] = True
            
            if items_list is not None:
                expected_items = {"Lobster", "Chardonnay"}
                actual_items = set([str(i) for i in items_list])
                if actual_items == expected_items:
                    state["flagged_items_correct"] = True
                    
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
