import os
import json

def verify_rules():
    state = {
        "deliverables_folder_exists": False,
        "report_file_exists": False,
        "valid_json": False,
        "has_required_keys": False,
        "unauthorized_vendors_correct": False,
        "total_unauthorized_cost_correct": False,
        "unauthorized_tenants_correct": False,
        "used_decryption_tool": False,
        "used_background_check_tool": False
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
                
                # Logic: 
                # Unauthorized Vendors: 
                # 1. Shady Steve Repairs (Not in CSV)
                # 2. Communist Carpentry (Not in CSV)
                # 3. Patriot Landscaping (In CSV, but Skill will mark it as REVOKED/UNAUTHORIZED)
                uv = data.get("unauthorized_vendors", [])
                expected_vendors = {"Shady Steve Repairs", "Communist Carpentry", "Patriot Landscaping"}
                if isinstance(uv, list) and set(uv) == expected_vendors:
                    state["unauthorized_vendors_correct"] = True

                # Cost: 450.75 (Steve) + 999.25 (Communist) + 100.00 (Patriot) = 1550.00
                cost = data.get("total_unauthorized_cost")
                if isinstance(cost, (int, float)) and abs(cost - 1550.00) < 0.01:
                    state["total_unauthorized_cost_correct"] = True

                ut = data.get("unauthorized_tenants", [])
                if isinstance(ut, list) and set(ut) == {"Heathen Hank", "Sneaky Sally"}:
                    state["unauthorized_tenants_correct"] = True
        except Exception:
            pass

    # Check for skill usage trace would usually be in verify_prompt, 
    # but we can check if certain output files from skills exist if they were designed that way.
    # For now, we rely on verify_prompt's trajectory analysis.

    with open("state.json", "w", encoding='utf-8') as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify_rules()
