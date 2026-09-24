import os
import json

def check():
    state = {
        "summary_file_exists": False,
        "is_valid_json": False,
        "outpatients_excluded": False,
        "all_residents_included": False,
        "pain_levels_correctly_formatted": False,
        "mindfulness_flags_correct": False
    }

    filepath = "organized_desk/residential_summary.json"
    if not os.path.exists(filepath):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f)
        return

    state["summary_file_exists"] = True

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["is_valid_json"] = True
    except:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f)
        return

    # Normalize data for flexible structural checking (list of dicts or dict of dicts)
    items = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                items.append(v)
            else:
                items.append({"name": k, "data": v})
    elif isinstance(data, list):
        items = data

    content_str = json.dumps(data).lower()

    # 1. Check exclusions (Sarah, Greg, Dave are outpatients)
    has_outpatients = any(name in content_str for name in ["sarah", "greg", "dave"])
    if not has_outpatients:
        state["outpatients_excluded"] = True

    # 2. Check inclusions (Arthur, Martha, Billy, Chloe are residents)
    has_residents = all(name in content_str for name in ["arthur", "martha", "billy", "chloe"])
    if has_residents:
        state["all_residents_included"] = True

    # Helper function to get patient-specific localized string representation
    def get_patient_data(name_substring):
        for item in items:
            item_str = json.dumps(item).lower()
            if name_substring in item_str:
                return item_str
        return ""

    arthur_str = get_patient_data("arthur")
    martha_str = get_patient_data("martha")
    billy_str = get_patient_data("billy")
    chloe_str = get_patient_data("chloe")

    # 3. Check pain levels (Should be stripped of fractions, just numbers)
    # Arthur: 6, Martha: 3, Billy: 8, Chloe: 5
    if "6/10" not in arthur_str and "6" in arthur_str and \
       "3/10" not in martha_str and "3" in martha_str and \
       "8/10" not in billy_str and "8" in billy_str and \
       "5/10" not in chloe_str and "5" in chloe_str:
        state["pain_levels_correctly_formatted"] = True

    # 4. Check mindfulness flags 
    # Keywords triggered: Arthur (stressed)->True, Martha (None)->False, Billy (tense)->True, Chloe (yoga)->True
    def is_true(s): return "true" in s or "yes" in s or "1" in s
    def is_false(s): return "false" in s or "no" in s or "0" in s

    if is_true(arthur_str) and is_false(martha_str) and is_true(billy_str) and is_true(chloe_str):
        state["mindfulness_flags_correct"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f)

if __name__ == "__main__":
    check()
