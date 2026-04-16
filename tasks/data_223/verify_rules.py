import os
import json

def verify():
    workspace = "workspace"
    json_path = os.path.join(workspace, "priority_stock.json")
    txt_path = os.path.join(workspace, "shift_note.txt")
    
    state = {
        "json_exists": False,
        "json_valid_format": False,
        "correct_priority_items": False,
        "correct_sorting": False,
        "txt_exists": False,
        "correct_counts_in_txt": False
    }
    
    if os.path.exists(json_path):
        state["json_exists"] = True
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state["json_valid_format"] = True
            
            if isinstance(data, list):
                item_ids = [item.get("item_id") for item in data if "item_id" in item]
                expected_ids = ["ITM001", "ITM006", "ITM002", "ITM007"]
                
                if set(item_ids) == set(expected_ids):
                    state["correct_priority_items"] = True
                
                if item_ids == expected_ids:
                    state["correct_sorting"] = True
        except Exception:
            pass
            
    if os.path.exists(txt_path):
        state["txt_exists"] = True
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            # There should be exactly 4 priority items and 4 junk items out of the 8 total
            if "4" in content:
                state["correct_counts_in_txt"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
