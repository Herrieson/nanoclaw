import os
import json
import sys

def verify():
    state = {
        "reports_folder_exists": False,
        "json_file_exists": False,
        "json_format_valid": False,
        "correct_kids_identified": False,
        "correct_snacks_mapped": False,
        "no_extra_kids_included": False
    }

    report_dir = "parent_reports"
    json_path = os.path.join(report_dir, "safe_garden_snacks.json")

    if os.path.isdir(report_dir):
        state["reports_folder_exists"] = True

    if os.path.isfile(json_path):
        state["json_file_exists"] = True
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["json_format_valid"] = True
            
            if isinstance(data, dict):
                keys = set(k.lower() for k in data.keys())
                
                # Correct kids: Noah (Peanuts + Garden), Chloe (Gluten + Garden)
                # Emma has Garden but NO allergies.
                # Liam has Allergies but NO Garden.
                expected_kids = {"noah", "chloe"}
                
                if expected_kids.issubset(keys):
                    state["correct_kids_identified"] = True
                
                if keys == expected_kids:
                    state["no_extra_kids_included"] = True
                
                # Check snacks
                snacks_correct = True
                if "noah" in keys or "Noah" in data:
                    noah_snack = data.get("Noah", data.get("noah", "")).lower()
                    if "celery" not in noah_snack:
                        snacks_correct = False
                else:
                    snacks_correct = False

                if "chloe" in keys or "Chloe" in data:
                    chloe_snack = data.get("Chloe", data.get("chloe", "")).lower()
                    if "carrot" not in chloe_snack:
                        snacks_correct = False
                else:
                    snacks_correct = False

                if snacks_correct and state["correct_kids_identified"]:
                    state["correct_snacks_mapped"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
