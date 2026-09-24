import os
import json
import math

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "total_cost_correct": False,
        "flagged_items_correct": False,
        "used_required_skills": False
    }

    report_path = "financial_forecast/dinner_budget.json"
    trace_path = "trace.jsonl"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Logic Calculation:
            # Lobster: Base 100, Current 120. Spike (20% > 15%). Cost: 120 * 1.2 = 144 USD
            # Oysters: Base 50, Current 52. No Spike. Cost: 52 USD
            # Chardonnay: Base 80 (from skill), Current 95 EUR. 
            #   95 EUR * 1.1 = 104.5 USD. Base 80 EUR * 1.1 = 88 USD. 
            #   Spike (104.5/88 = 1.1875 > 15%). Cost: 104.5 * 1.2 = 125.4 USD
            # Pinot Noir: Base 120 (from skill), Current 125 USD. No Spike. Cost: 125 USD
            # Total: 144 + 52 + 125.4 + 125 = 446.4
            
            cost_val = data.get("total_usd_cost") or data.get("total_cost")
            if cost_val and math.isclose(float(cost_val), 446.4, rel_tol=1e-3):
                state["total_cost_correct"] = True
            
            flagged = data.get("flagged_items", [])
            expected_flagged = {"Lobster", "Chardonnay"}
            if set(flagged) == expected_flagged:
                state["flagged_items_correct"] = True
        except:
            pass

    if os.path.exists(trace_path):
        with open(trace_path, "r") as f:
            content = f.read()
            if "global_inflation_lookup_skill" in content and "pdf_data_extractor" in content:
                state["used_required_skills"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
