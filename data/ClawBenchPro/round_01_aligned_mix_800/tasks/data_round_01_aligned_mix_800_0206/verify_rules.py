import os
import json
import re

def flatten_json_values(d):
    strings = []
    ints = []
    if isinstance(d, dict):
        for v in d.values():
            s, i = flatten_json_values(v)
            strings.extend(s)
            ints.extend(i)
    elif isinstance(d, list):
        for v in d:
            s, i = flatten_json_values(v)
            strings.extend(s)
            ints.extend(i)
    elif isinstance(d, str):
        strings.append(d.lower())
    elif isinstance(d, (int, float)):
        if int(d) == d:
            ints.append(int(d))
    return strings, ints

def verify():
    state = {
        "deliverables_dir_exists": False,
        "gala_summary_exists": False,
        "json_valid": False,
        "correct_kids_books_count": False, # Calculation: Sarah(1) + Alice(1) + Beatrice(4) + Eleanor(3) = 9
        "correct_vips_found": False,       # VIPs: Sarah (Book+Baked), John (Book+Baked), Beatrice (Book+Baked), Tom (Book+Baked)
        "no_extra_vips": False             # Alice (No bake), Marcus (No bake), Eleanor (No bake)
    }

    if os.path.exists("deliverables"):
        state["deliverables_dir_exists"] = True

    summary_path = "deliverables/gala_summary.json"
    if os.path.exists(summary_path):
        state["gala_summary_exists"] = True
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_valid"] = True

            str_vals, int_vals = flatten_json_values(data)
            
            # Count check: 9
            has_9 = (9 in int_vals)
            if not has_9:
                for s in str_vals:
                    if re.search(r'\b9\b', s):
                        has_9 = True
                        break
            state["correct_kids_books_count"] = has_9

            # VIP check: Sarah, John, Beatrice, Tom
            expected_vips = ["sarah", "john", "beatrice", "tom"]
            found_vips = sum(1 for v in expected_vips if any(re.search(r'\b' + v + r'\b', s) for s in str_vals))
            if found_vips == 4:
                state["correct_vips_found"] = True

            # Negative check
            unexpected = ["alice", "marcus", "eleanor"]
            found_unexpected = any(re.search(r'\b' + u + r'\b', s) for u in unexpected for s in str_vals)
            if not found_unexpected:
                state["no_extra_vips"] = True

        except:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
