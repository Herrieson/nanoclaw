import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "json_report_exists": False,
        "json_is_valid": False,
        "violators_correctly_identified": False,
        "false_positives_avoided": False,
        "memo_draft_exists": False
    }

    deliverables_path = "deliverables"
    if os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        # Check JSON
        json_files = [f for f in os.listdir(deliverables_path) if f.endswith('.json')]
        if json_files:
            state["json_report_exists"] = True
            json_path = os.path.join(deliverables_path, json_files[0])
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state["json_is_valid"] = True
                    
                    data_str = json.dumps(data).lower()
                    
                    # Barnes and Davis are violators (>20% admin)
                    if "barnes" in data_str and "davis" in data_str:
                        state["violators_correctly_identified"] = True
                    
                    # Adams and Chen are compliant
                    if "adams" not in data_str and "chen" not in data_str:
                        state["false_positives_avoided"] = True
            except:
                pass
                
        # Check Memo
        md_files = [f for f in os.listdir(deliverables_path) if f.endswith('.md')]
        if md_files:
            md_path = os.path.join(deliverables_path, md_files[0])
            if os.path.getsize(md_path) > 50: # Basic check that it's not empty
                state["memo_draft_exists"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
