import os
import json
import sys

def verify_rules():
    state = {
        "deliverables_folder_exists": False,
        "report_file_exists": False,
        "valid_json": False,
        "has_required_keys": False,
        "unauthorized_vendors_correct": False,
        "total_unauthorized_cost_correct": False,
        "unauthorized_tenants_correct": False
    }

    folder_path = "audit_deliverables"
    report_path = os.path.join(folder_path, "discrepancy_report.json")

    if os.path.isdir(folder_path):
        state["deliverables_folder_exists"] = True

    if os.path.isfile(report_path):
        state["report_file_exists"] = True
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state["valid_json"] = True

            required_keys = {"unauthorized_vendors", "total_unauthorized_cost", "unauthorized_tenants"}
            
            if isinstance(data, dict) and required_keys.issubset(set(data.keys())):
                state["has_required_keys"] = True

                # Check unauthorized vendors
                uv = data.get("unauthorized_vendors", [])
                if isinstance(uv, list) and set(uv) == {"Shady Steve Repairs", "Communist Carpentry"}:
                    state["unauthorized_vendors_correct"] = True

                # Check total unauthorized cost (450.75 + 999.25 = 1450.00)
                cost = data.get("total_unauthorized_cost")
                if isinstance(cost, (int, float)) and (cost == 1450.00 or cost == 1450):
                    state["total_unauthorized_cost_correct"] = True

                # Check unauthorized tenants
                ut = data.get("unauthorized_tenants", [])
                if isinstance(ut, list) and set(ut) == {"Heathen Hank", "Sneaky Sally"}:
                    state["unauthorized_tenants_correct"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding='utf-8') as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify_rules()
