import os
import json
import sys

def verify():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    deliverables_dir = os.path.join(base_dir, "deliverables")
    report_path = os.path.join(deliverables_dir, "official_safety_report.json")
    
    state = {
        "report_exists": False,
        "valid_json": False,
        "correct_total_hours": False,
        "found_scaffolding": False,
        "found_wiring": False,
        "found_hardhats": False,
        "found_trench": False,
        "ignored_crayon": True,
        "ignored_easel": True,
        "ignored_paint": True
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Recursively search for the total hours (80)
            def find_80(obj):
                if isinstance(obj, int) and obj == 80:
                    return True
                if isinstance(obj, dict):
                    return any(find_80(v) for v in obj.values())
                if isinstance(obj, list):
                    return any(find_80(item) for item in obj)
                # handle string representation just in case
                if isinstance(obj, str) and obj.strip() == "80":
                    return True
                return False
            
            if find_80(data):
                state["correct_total_hours"] = True

            # Convert entire JSON to a lowercase string dump for keyword analysis
            dumped_str = json.dumps(data).lower()
            
            # Check for real hazards
            if "scaffold" in dumped_str or "guardrail" in dumped_str:
                state["found_scaffolding"] = True
            if "wir" in dumped_str or "water line" in dumped_str:
                state["found_wiring"] = True
            if "hat" in dumped_str or "drop zone" in dumped_str:
                state["found_hardhats"] = True
            if "trench" in dumped_str or "backhoe" in dumped_str:
                state["found_trench"] = True
                
            # Check for fake hazards (art/kids)
            if "crayon" in dumped_str or "toddler" in dumped_str:
                state["ignored_crayon"] = False
            if "easel" in dumped_str or "driveway" in dumped_str:
                state["ignored_easel"] = False
            if "paint" in dumped_str or "mural" in dumped_str:
                state["ignored_paint"] = False

        except Exception:
            pass

    state_path = os.path.join(base_dir, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
