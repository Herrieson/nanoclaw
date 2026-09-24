import os
import json
import re

def verify():
    state = {
        "output_dir_exists": False,
        "action_plan_exists": False,
        "chart_exists": False,
        "correct_trails_identified": False,
        "correct_volunteers_identified": False,
        "recommended_tools_included": False,
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
            
            # Hazard > 3: Bear Creek (5), Summit Path (4), Canyon Descent (6)
            dangerous_trails = [t["name"].lower() for t in data.get("dangerous_trails", [])]
            expected_trails = ["bear creek", "summit path", "canyon descent"]
            if all(t in dangerous_trails for t in expected_trails) and len(dangerous_trails) == 3:
                state["correct_trails_identified"] = True

            # Recommended Tools (from Skill mock logic)
            tools = [t.get("recommended_tool", "").lower() for t in data.get("dangerous_trails", [])]
            if "chainsaw" in tools and "gravel_truck" in tools and "heavy_excavator" in tools:
                state["recommended_tools_included"] = True

            # Volunteers: Samuel, Marie
            volunteers = [v.lower() for v in data.get("capable_volunteers", [])]
            if "samuel" in volunteers and "marie" in volunteers and len(volunteers) == 2:
                state["correct_volunteers_identified"] = True
                
        except Exception:
            pass

    chart_path = os.path.join("output", "hazard_chart.txt")
    if os.path.exists(chart_path):
        state["chart_exists"] = True
        try:
            with open(chart_path, "r", encoding="utf-8") as f:
                content = f.read()
            if re.search(r'([*#=\-+|█▇▆▅▄▃▂ ]{3,})', content):
                state["chart_is_visual"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
