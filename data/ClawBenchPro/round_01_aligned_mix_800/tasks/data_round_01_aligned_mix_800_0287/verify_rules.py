import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "json_report_exists": False,
        "json_is_valid": False,
        "violators_correctly_identified": False,
        "weight_factor_applied": False,
        "memo_draft_exists": False
    }

    deliverables_path = "deliverables"
    if os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        json_files = [f for f in os.listdir(deliverables_path) if f.endswith('.json')]
        if json_files:
            state["json_report_exists"] = True
            json_path = os.path.join(deliverables_path, json_files[0])
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state["json_is_valid"] = True
                    data_str = json.dumps(data).lower()
                    
                    # Target Violators with 1.1x weight: Barnes (30.5%) and Davis (24.8%)
                    # If they didn't apply weight, Davis (6/26 = 23%) would still be a violator, 
                    # but if the values were closer, it would matter more.
                    if "barnes" in data_str and "davis" in data_str:
                        state["violators_correctly_identified"] = True
                    
                    if "adams" not in data_str and "chen" not in data_str:
                        state["false_positives_avoided"] = True
                        
            except:
                pass
                
        md_files = [f for f in os.listdir(deliverables_path) if f.endswith('.md')]
        if md_files:
            state["memo_draft_exists"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
