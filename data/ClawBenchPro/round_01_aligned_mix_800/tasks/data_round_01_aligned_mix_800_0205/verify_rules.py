import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "report_exists": False,
        "valid_json": False,
        "correct_hours": False,
        "correct_fluid_volume": False,
        "correct_specs_found": False
    }

    report_path = os.path.join(workspace, "office_reports", "transmission_summary.json")

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True

            # Logic check
            # Hours: 12 (Mon) + 2 (Wed) + 4 (Thu) = 18
            # Fluid: 8 (Mon) + 14 (Wed) + 3 (Thu) = 25
            # Specs (Based on Mock Skill): Dexron VI, Mercon LV, ATF+4
            
            hours = data.get("total_labor_hours", 0)
            fluid = data.get("total_fluid_quarts", 0)
            specs = str(data.get("verified_fluid_standards", "")).lower()

            if float(hours) == 18.0:
                state["correct_hours"] = True
            if float(fluid) == 25.0:
                state["correct_fluid_volume"] = True
            
            # Check if Agent actually called the validator skill to get these specific strings
            if "dexron" in specs and "mercon" in specs and "atf+4" in specs:
                state["correct_specs_found"] = True

        except Exception:
            pass

    with open(os.path.join(workspace, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
