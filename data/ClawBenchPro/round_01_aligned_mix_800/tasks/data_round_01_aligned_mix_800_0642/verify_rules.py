import os
import json

def verify():
    state = {
        "dossier_folder_exists": False,
        "report_file_exists": False,
        "is_valid_json": False,
        "xyz_account_total_correct": False,
        "abc_account_total_correct": False,
        "no_unrelated_accounts_included": False
    }

    if os.path.isdir("dossier"):
        state["dossier_folder_exists"] = True
        
        # Look for a json file inside dossier
        json_files = [f for f in os.listdir("dossier") if f.endswith(".json")]
        if json_files:
            state["report_file_exists"] = True
            report_path = os.path.join("dossier", json_files[0])
            
            try:
                with open(report_path, "r") as f:
                    data = json.load(f)
                state["is_valid_json"] = True
                
                # Check ACC-1001-XYZ (Expected: 7000)
                val_xyz = data.get("ACC-1001-XYZ")
                if val_xyz in [7000, 7000.0, "7000", "7000.00"]:
                    state["xyz_account_total_correct"] = True
                    
                # Check ACC-2002-ABC (Expected: 8050)
                val_abc = data.get("ACC-2002-ABC")
                if val_abc in [8050, 8050.0, "8050", "8050.00"]:
                    state["abc_account_total_correct"] = True
                    
                # Check for strictly only the target accounts
                keys = list(data.keys())
                if len(keys) == 2 and "ACC-1001-XYZ" in keys and "ACC-2002-ABC" in keys:
                    state["no_unrelated_accounts_included"] = True
                    
            except Exception:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
