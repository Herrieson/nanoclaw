import os
import json

def verify():
    state = {
        "plan_exists": False,
        "json_valid": False,
        "ingredients_scaled_correctly": False,
        "party_budget_correct": False,
        "total_cost_correct": False,
        "under_budget_boolean_correct": False
    }

    plan_path = "cookout_plan/party_summary.json"
    
    if os.path.exists(plan_path):
        state["plan_exists"] = True
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_valid"] = True

            # 1. Check if ingredients are scaled by 5 (25 people / 5 servings)
            ings = data.get("ingredients", {})
            if (ings.get("beef_chuck_lbs") == 15 and
                ings.get("dried_guajillo_chiles") == 30 and
                ings.get("garlic_cloves") == 20 and
                ings.get("onion") == 5 and
                ings.get("corn_tortillas_pack") == 5):
                state["ingredients_scaled_correctly"] = True

            # 2. Check Party Budget
            # Income (4000) - Expenses (1200+450+200+300 = 2150) = 1850 left.
            # 10% of 1850 = 185.0
            budget = data.get("party_budget")
            if budget is not None and abs(float(budget) - 185.0) < 0.01:
                state["party_budget_correct"] = True

            # 3. Check Total Cost
            # Based on mock API strict returns:
            # (15 * 6.5) + (30 * 0.2) + (20 * 0.1) + (5 * 0.8) + (5 * 3.0) = 97.5 + 6 + 2 + 4 + 15 = 124.5
            cost = data.get("total_cost")
            if cost is not None and abs(float(cost) - 124.5) < 0.01:
                state["total_cost_correct"] = True

            # 4. Check Under Budget boolean (124.5 <= 185.0, so True)
            if data.get("under_budget") is True:
                state["under_budget_boolean_correct"] = True

        except Exception:
            pass 

    # Write objective state probe to state.json
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
