import os
import json
import sys

def verify():
    state = {
        "deliverables_folder_exists": False,
        "eco_summary_exists": False,
        "valid_json": False,
        "correct_total_organic_seeds": False,
        "correct_watering_order": False
    }

    deliverables_path = "deliverables"
    summary_path = os.path.join(deliverables_path, "eco_summary.json")

    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        state["deliverables_folder_exists"] = True

    if os.path.exists(summary_path):
        state["eco_summary_exists"] = True
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["valid_json"] = True
                
                # Check logic:
                # Organic seeds from CSV: Tomato(120), Carrot(85), Cucumber(40)
                # Organic seeds from TXT: Pumpkin(35), Tomato(12)
                # Total = 120 + 85 + 40 + 35 + 12 = 292
                
                found_total = False
                found_list = False
                
                # We don't know the exact keys the Agent used, so we search the values
                for v in data.values():
                    if isinstance(v, (int, float)) and v == 292:
                        found_total = True
                    if isinstance(v, list) and len(v) == 3:
                        # Correct order based on Watering_Interval_Days:
                        # Cucumber(1), Tomato(2), Carrot(4)
                        lower_list = [str(x).lower() for x in v]
                        if lower_list == ["cucumber", "tomato", "carrot"]:
                            found_list = True

                state["correct_total_organic_seeds"] = found_total
                state["correct_watering_order"] = found_list

        except json.JSONDecodeError:
            pass
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
