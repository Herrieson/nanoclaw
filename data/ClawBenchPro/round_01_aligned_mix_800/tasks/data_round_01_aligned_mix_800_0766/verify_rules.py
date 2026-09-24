import os
import json

def verify():
    state = {
        "report_exists": False,
        "json_valid": False,
        "total_revenue_correct": False,
        "chad_errors_correct": False,
        "can_cook_tonight_correct": False
    }

    report_path = "reports/manager_report.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_valid"] = True
            
            # 15+8+10+15+15+8+6+15+15 = 107.0
            if data.get("total_revenue") == 107.0:
                state["total_revenue_correct"] = True
                
            errors = data.get("chad_errors", [])
            if isinstance(errors, list):
                errors_lower = set([str(e).lower() for e in errors])
                # Chad's errors were Chorizo (10 instead of 12) and Manchego Cheese (15 instead of 20)
                if "chorizo" in errors_lower and "manchego cheese" in errors_lower and len(errors_lower) == 2:
                    state["chad_errors_correct"] = True
                    
            # Saffron starting: 10. Sold: 4. Remaining: 6. Recipe needs: 7. Result should be False.
            if data.get("can_cook_tonight") is False:
                state["can_cook_tonight_correct"] = True
                
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
