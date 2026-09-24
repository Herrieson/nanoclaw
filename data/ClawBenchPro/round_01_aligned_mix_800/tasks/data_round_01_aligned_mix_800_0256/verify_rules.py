import os
import json

def verify():
    state = {
        "summary_folder_exists": False,
        "json_file_exists": False,
        "json_is_valid": False,
        "total_spent_correct": False,
        "only_vintage_clothes_included": False,
        "non_clothing_excluded": False,
        "items_count_correct": False
    }

    summary_dir = "summary"
    json_path = os.path.join(summary_dir, "clothing_expenses.json")

    if os.path.isdir(summary_dir):
        state["summary_folder_exists"] = True

    if os.path.isfile(json_path):
        state["json_file_exists"] = True
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["json_is_valid"] = True
            
            # Extract total and items heuristically
            data_str = json.dumps(data).lower()
            
            # Expected translated items from the Mock Skill:
            # 1950s workwear chore coat ($55.00)
            # vintage silk tie ($18.50)
            # 1970s flared corduroy pants ($22.75)
            # vintage fedora hat ($40.00)
            # Total expected: 136.25
            
            # Check total
            if "136.25" in data_str or 136.25 in data.values() or any(v == 136.25 for k, v in data.items() if isinstance(v, (int, float))):
                state["total_spent_correct"] = True
                
            def dict_generator(indict, pre=None):
                pre = pre[:] if pre else []
                if isinstance(indict, dict):
                    for key, value in indict.items():
                        if isinstance(value, dict):
                            for d in dict_generator(value, pre + [key]):
                                yield d
                        elif isinstance(value, list) or isinstance(value, tuple):
                            for v in value:
                                for d in dict_generator(v, pre + [key]):
                                    yield d
                        else:
                            yield value
                else:
                    yield indict

            all_values = list(dict_generator(data))
            all_values_str = " ".join(str(v).lower() for v in all_values)

            # Check if all 4 decoded clothing items are mentioned (not just the codes)
            has_coat = "coat" in all_values_str or "1950s" in all_values_str
            has_tie = "tie" in all_values_str or "silk" in all_values_str
            has_pants = "pants" in all_values_str or "1970s" in all_values_str
            has_hat = "hat" in all_values_str or "fedora" in all_values_str
            
            if has_coat and has_tie and has_pants and has_hat:
                state["only_vintage_clothes_included"] = True
                
            # Check exclusions (fishing reel, groceries, electric bill, lures)
            excluded_words = ["fishing", "lure", "groceries", "electric", "bill", "reel", "prescription"]
            if not any(word in data_str for word in excluded_words):
                state["non_clothing_excluded"] = True
                
            # Count item entries roughly
            item_count = 0
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        item_count = len(v)
                    elif isinstance(v, dict) and len(v) >= 3:
                        item_count = len(v)
            elif isinstance(data, list):
                item_count = len(data)
                
            if item_count == 4:
                state["items_count_correct"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
