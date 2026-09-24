import os
import json
import re

def verify():
    # The objective probe: only checking physical facts, zero score calculations.
    state = {
        "output_dir_exists": False,
        "action_plan_exists": False,
        "chart_exists": False,
        "correct_trails_identified": False,
        "correct_volunteers_identified": False,
        "chart_is_visual": False,
        "json_is_valid": False
    }

    if os.path.exists("output") and os.path.isdir("output"):
        state["output_dir_exists"] = True

    plan_path = os.path.join("output", "action_plan.json")
    if os.path.exists(plan_path):
        state["action_plan_exists"] = True
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_is_valid"] = True
            
            content = str(data).lower()
            
            # Hazard > 3 implies: Bear Creek, Summit Path, Canyon Descent
            # Should NOT include: Pine Ridge, Lake Loop, Meadow Trail
            has_dangerous = all(t in content for t in ["bear creek", "summit path", "canyon descent"])
            has_safe = any(t in content for t in ["pine ridge", "lake loop", "meadow trail"])
            
            if has_dangerous and not has_safe:
                state["correct_trails_identified"] = True

            # Volunteers with "clearing": Samuel, Marie
            # Should NOT include: David, Chloe, Jerome
            has_clearers = all(v in content for v in ["samuel", "marie"])
            has_others = any(v in content for v in ["david", "chloe", "jerome"])
            
            if has_clearers and not has_others:
                state["correct_volunteers_identified"] = True
                
        except Exception:
            pass

    chart_path = os.path.join("output", "hazard_chart.txt")
    if os.path.exists(chart_path):
        state["chart_exists"] = True
        try:
            with open(chart_path, "r", encoding="utf-8") as f:
                chart_content = f.read()
            
            # Look for visual elements like multiple asterisks, hashes, dashes, or blocks
            if re.search(r'([*#=\-+|█▇▆▅▄▃▂ ]{3,})', chart_content):
                state["chart_is_visual"] = True
        except Exception:
            pass

    # Strictly outputting to state.json
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
