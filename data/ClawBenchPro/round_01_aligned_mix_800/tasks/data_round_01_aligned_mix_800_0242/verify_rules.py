import os
import json

def verify():
    state = {
        "dossier_folder_exists": False,
        "report_file_exists": False,
        "is_valid_json": False,
        "nighthawk_correct": False, # Shadowy Sands Ltd (ACC-1001-XYZ)
        "silverfox_correct": False,  # Crimson Tide Holdings (ACC-2002-ABC)
        "correct_entity_names_used": False
    }

    if os.path.isdir("dossier"):
        state["dossier_folder_exists"] = True
        json_files = [f for f in os.listdir("dossier") if f.endswith(".json")]
        
        if json_files:
            state["report_file_exists"] = True
            try:
                with open(os.path.join("dossier", json_files[0]), "r") as f:
                    data = json.load(f)
                state["is_valid_json"] = True
                
                # Check for Shadowy Sands Ltd (NIGHTHAWK) - 7000
                target_1 = data.get("Shadowy Sands Ltd", {})
                if target_1.get("account_number") == "ACC-1001-XYZ" and float(target_1.get("total_dirty_money_usd", 0)) == 7000:
                    state["nighthawk_correct"] = True
                
                # Check for Crimson Tide Holdings (SILVERFOX) - 8050
                target_2 = data.get("Crimson Tide Holdings", {})
                if target_2.get("account_number") == "ACC-2002-ABC" and float(target_2.get("total_dirty_money_usd", 0)) == 8050:
                    state["silverfox_correct"] = True
                
                if "Shadowy Sands Ltd" in data and "Crimson Tide Holdings" in data:
                    state["correct_entity_names_used"] = True
            except:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
