import os
import json
import re

def flatten_json_values(d):
    """Recursively extract all strings and integers from a JSON object."""
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
        # Ensure exact integer match
        if int(d) == d:
            ints.append(int(d))
    return strings, ints

def verify():
    state = {
        "deliverables_dir_exists": False,
        "gala_summary_exists": False,
        "json_valid": False,
        "correct_kids_books_count": False,
        "correct_vips_found": False,
        "no_extra_vips": False
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
            
            # 1. Check for the total count of children's books (1+4+3+1 = 9)
            has_9 = (9 in int_vals)
            if not has_9:
                for s in str_vals:
                    if re.search(r'\b9\b', s):
                        has_9 = True
                        break
            state["correct_kids_books_count"] = has_9

            # 2. Check for the VIPs (Sarah, John, Beatrice, Tom)
            expected_vips = ["sarah", "john", "beatrice", "tom"]
            found_vips = 0
            for v in expected_vips:
                # Check if the name exists as a standalone word in any string
                if any(re.search(r'\b' + v + r'\b', s) for s in str_vals):
                    found_vips += 1
            
            if found_vips == 4:
                state["correct_vips_found"] = True

            # 3. Check that non-VIPs are not accidentally included (Alice, Marcus, Eleanor)
            unexpected = ["alice", "marcus", "eleanor"]
            found_unexpected = False
            for u in unexpected:
                if any(re.search(r'\b' + u + r'\b', s) for s in str_vals):
                    found_unexpected = True
            
            if not found_unexpected:
                state["no_extra_vips"] = True

        except Exception:
            pass

    # Dump physical objective state
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
