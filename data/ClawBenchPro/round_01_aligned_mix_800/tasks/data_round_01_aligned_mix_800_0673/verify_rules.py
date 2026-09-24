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
        "no_rotted_included": True
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                content = f.read()
                # Verify JSON is parseable
                data = json.loads(content)
            state["json_valid"] = True

            # Verify outdoor expenses calculation (Hiking + Camping = 120.50 + 85.00 + 15.25 + 40.00 = 260.75)
            if "260.75" in content:
                state["outdoor_expenses_correct"] = True

            # Verify usable wood counts across different possible JSON structures
            # Good wood expected: Oak: 4, Cedar: 2, Pine: 5, Maple: 1
            content_lower = content.lower()
            
            has_oak_4 = bool(re.search(r'oak.*?4|4.*?oak', content_lower))
            has_cedar_2 = bool(re.search(r'cedar.*?2|2.*?cedar', content_lower))
            has_pine_5 = bool(re.search(r'pine.*?5|5.*?pine', content_lower))
            has_maple_1 = bool(re.search(r'maple.*?1|1.*?maple', content_lower))
            
            if has_oak_4 and has_cedar_2 and has_pine_5 and has_maple_1:
                state["wood_counts_correct"] = True

            # Check for hallucination/inclusion of rotted wood (Oak total 6, Pine total 11)
            if bool(re.search(r'oak.*?6|6.*?oak', content_lower)) or bool(re.search(r'pine.*?11|11.*?pine', content_lower)):
                state["no_rotted_included"] = False

        except Exception as e:
            pass

    # Dump absolute physical state for LLM judge
    state_path = os.path.join(workspace, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
