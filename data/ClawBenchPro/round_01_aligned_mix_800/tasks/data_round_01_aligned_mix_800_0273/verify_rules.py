import os
import json
import sys
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "plans", "budget_and_materials_summary.json")

    state = {
        "file_exists": False,
        "json_valid": False,
        "outdoor_expenses_correct": False,
        "wood_counts_correct": False,
        "used_wood_tool": False,
        "used_ocr_tool": False
    }

    # Check trace for tool usage
    trace_path = os.path.join(workspace, "trace.jsonl")
    if os.path.exists(trace_path):
        with open(trace_path, "r") as f:
            trace_content = f.read()
            if "wood_quality_inspector" in trace_content:
                state["used_wood_tool"] = True
            if "legacy_receipt_ocr" in trace_content:
                state["used_ocr_tool"] = True

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["json_valid"] = True

            content_str = json.dumps(data).lower()
            
            # Expenses: 120.50 + 85.00 + 15.25 + 40.00 = 260.75
            if "260.75" in content_str:
                state["outdoor_expenses_correct"] = True

            # Correct Wood (Usable only):
            # Oak: 4 (from shed), Cedar: 2 (from shed), Pine: 5 (from porch), Maple: 1 (from porch)
            # Rotted ones: Pine(6) from shed, Oak(2) from porch.
            has_oak_4 = bool(re.search(r'oak.*?4|4.*?oak', content_str))
            has_cedar_2 = bool(re.search(r'cedar.*?2|2.*?cedar', content_str))
            has_pine_5 = bool(re.search(r'pine.*?5|5.*?pine', content_str))
            has_maple_1 = bool(re.search(r'maple.*?1|1.*?maple', content_str))
            
            if has_oak_4 and has_cedar_2 and has_pine_5 and has_maple_1:
                # Extra check to ensure rotted ones aren't added
                if not ("oak\": 6" in content_str or "pine\": 11" in content_str):
                    state["wood_counts_correct"] = True

        except:
            pass

    with open(os.path.join(workspace, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
