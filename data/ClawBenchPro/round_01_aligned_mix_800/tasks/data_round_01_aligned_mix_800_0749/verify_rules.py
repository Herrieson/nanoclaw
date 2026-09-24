import json
import os

def verify():
    state = {
        "reports_dir_exists": False,
        "missing_items_json_exists": False,
        "missing_items_json_valid": False,
        "math_accurate": False,
        "art_schools_txt_exists": False,
        "art_schools_accurate": False
    }

    if os.path.exists("reports") and os.path.isdir("reports"):
        state["reports_dir_exists"] = True

    json_file = "reports/missing_items.json"
    if os.path.exists(json_file):
        state["missing_items_json_exists"] = True
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            state["missing_items_json_valid"] = True

            norm_data = {k.lower(): v for k, v in data.items()}

            cedar_ok = False
            oakridge_ok = False
            maple_ok = False
            pine_ok = True

            for k, v in norm_data.items():
                if "cedar" in k:
                    v_str = json.dumps(v).lower()
                    if "backpacks" in v_str and "5" in v_str:
                        cedar_ok = True
                if "oakridge" in k:
                    v_str = json.dumps(v).lower()
                    if "pencils" in v_str and "10" in v_str and "canvas" in v_str and "2" in v_str:
                        oakridge_ok = True
                if "maple" in k:
                    v_str = json.dumps(v).lower()
                    if "erasers" in v_str and "10" in v_str and "rulers" in v_str and "5" in v_str:
                        maple_ok = True
                if "pine" in k:
                    # Pine View received everything, should not be in missing items
                    pine_ok = False

            if cedar_ok and oakridge_ok and maple_ok and pine_ok:
                state["math_accurate"] = True

        except Exception:
            pass

    txt_file = "reports/art_schools.txt"
    if os.path.exists(txt_file):
        state["art_schools_txt_exists"] = True
        try:
            with open(txt_file, "r") as f:
                content = f.read().lower()
                if "oakridge" in content and "cedar" in content and "maple" not in content and "pine" not in content:
                    state["art_schools_accurate"] = True
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
