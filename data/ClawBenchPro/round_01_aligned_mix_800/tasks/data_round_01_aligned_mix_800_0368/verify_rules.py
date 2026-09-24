import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "json_report_exists": False,
        "parsed_json_successfully": False,
        "correct_total_count": False,
        "all_target_names_found": False,
        "no_extra_names_found": False
    }
    
    if os.path.exists("deliverables") and os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        
        files = os.listdir("deliverables")
        json_files = [f for f in files if f.endswith(".json")]
        
        if json_files:
            state["json_report_exists"] = True
            report_path = os.path.join("deliverables", json_files[0])
            
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                state["parsed_json_successfully"] = True
                
                content_str = json.dumps(data).lower()
                
                # The CRM mapping resolves ID_881->Alice Smith, ID_883->Bob Lee, ID_885->David Kim, ID_887->George Miller
                target_names = ["alice smith", "bob lee", "david kim", "george miller"]
                noise_names = ["eve johnson", "charlie davis", "fiona gallagher"]
                
                all_targets_present = all(name in content_str for name in target_names)
                if all_targets_present:
                    state["all_target_names_found"] = True
                    
                no_noise_present = all(name not in content_str for name in noise_names)
                if no_noise_present:
                    state["no_extra_names_found"] = True
                
                if "4" in content_str or data.get("count") == 4 or data.get("total") == 4 or len(data.get("entries", [])) == 4 or len(data.get("feedback", [])) == 4:
                    state["correct_total_count"] = True
                    
            except Exception:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
