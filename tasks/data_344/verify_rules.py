import os
import json
import re

def verify():
    workspace = "."
    md_file_path = os.path.join(workspace, "budget_recipes.md")
    
    state = {
        "file_exists": False,
        "has_mapo_tofu": False,
        "has_tomato_egg": False,
        "has_hong_shao_rou": False,
        "no_buddha_jumps": True,
        "correct_mapo_cost": False,
        "correct_tomato_cost": False,
        "correct_hong_shao_cost": False,
        "correct_format": False
    }

    if not os.path.exists(md_file_path):
        with open(os.path.join(workspace, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Expected Costs:
    # Mapo Tofu: 2.5 + 3.0 + 5.0 + 0.5 + 1.5 = 12.50
    # Tomato Egg: 2.0 + 1.5 + 0.5 + 0.2 + 0.1 = 4.30
    # Hong Shao Rou: 8.0 + 1.2 + 1.0 + 0.5 + 0.5 = 11.20
    # Buddha Jumps: 50 + 40 + 20 + 5 = 115.00 (>15, should be omitted)

    if "Mapo Tofu" in content:
        state["has_mapo_tofu"] = True
    if "Tomato Egg Stir-fry" in content:
        state["has_tomato_egg"] = True
    if "Hong Shao Rou" in content:
        state["has_hong_shao_rou"] = True
    if "Buddha Jumps Over the Wall" in content:
        state["no_buddha_jumps"] = False

    if re.search(r"Total Cost:\s*\$12\.50", content):
        state["correct_mapo_cost"] = True
    if re.search(r"Total Cost:\s*\$4\.30", content):
        state["correct_tomato_cost"] = True
    if re.search(r"Total Cost:\s*\$11\.20", content):
        state["correct_hong_shao_cost"] = True

    # Check formatting: ATX level 2 header and bullet points
    if re.search(r"##\s+Mapo Tofu", content) and re.search(r"-\s+Tofu", content):
        state["correct_format"] = True

    with open(os.path.join(workspace, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
