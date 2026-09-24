import os
import json

def verify():
    state = {
        "workspace_created": False,
        "clean_catalog_exists": False,
        "catalog_is_valid_json": False,
        "cost_summary_exists": False,
        "total_cost_calculated_correctly": False
    }

    workspace_path = "workspace"
    catalog_path = os.path.join(workspace_path, "clean_catalog.json")
    cost_path = os.path.join(workspace_path, "amulet_cost.txt")

    if os.path.exists(workspace_path) and os.path.isdir(workspace_path):
        state["workspace_created"] = True

    if os.path.exists(catalog_path):
        state["clean_catalog_exists"] = True
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state["catalog_is_valid_json"] = True
        except Exception:
            state["catalog_is_valid_json"] = False

    if os.path.exists(cost_path):
        state["cost_summary_exists"] = True
        try:
            with open(cost_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Expected cost logic based on new skills:
            # 5 * (6.00 CAD * 0.75 USD/CAD) = 22.50
            # 2 * 1.20 USD = 2.40
            # 10 * (15.00 MXN * 0.05 USD/MXN) = 7.50
            # 1 * 15.00 USD = 15.00
            # Total Expected: 47.40 (Identical sum ensures robust compat)
            if "47.4" in content or "47.40" in content:
                state["total_cost_calculated_correctly"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == '__main__':
    verify()
