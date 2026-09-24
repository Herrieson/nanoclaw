import os
import json
import re

def verify():
    # Conversion Logic for calculation:
    # 1 handful = 0.5 units
    # 1 scoop = 1.0 units
    
    # ThreeSistersStew: 
    # Corn: 3 handfuls * 0.5 = 1.5 units. Cost: 1.5*0.5=0.75, Cal: 1.5*50=75
    # Beans: 2 scoops * 1.0 = 2.0 units. Cost: 2.0*0.3=0.60, Cal: 2.0*80=160
    # Squash: 1.0 units. Cost: 1.0*0.8=0.80, Cal: 1.0*40=40
    # Total Cost: 0.75 + 0.60 + 0.80 = 2.15
    # Total Cal: 75 + 160 + 40 = 275

    # BisonSliders:
    # Bison: 4 handfuls * 0.5 = 2.0 units. Cost: 2.0*3.0=6.0, Cal: 2.0*200=400
    # Buns: 1.0 units. Cost: 1.0*0.5=0.5, Cal: 1.0*150=150
    # Sauce: 1 scoop * 1.0 = 1.0 units. Cost: 1.0*0.2=0.2, Cal: 1.0*50=50
    # Total Cost: 6.0 + 0.5 + 0.2 = 6.70
    # Total Cal: 400 + 150 + 50 = 600

    state = {
        "presentation_folder_exists": False,
        "stew_cost_correct": False,
        "stew_calories_correct": False,
        "sliders_cost_correct": False,
        "sliders_calories_correct": False,
        "skill_used_heritage": False
    }

    target_dir = "presentation"
    if os.path.exists(target_dir):
        state["presentation_folder_exists"] = True
        all_content = ""
        for filename in os.listdir(target_dir):
            with open(os.path.join(target_dir, filename), "r") as f:
                all_content += f.read()
        
        if "2.15" in all_content: state["stew_cost_correct"] = True
        if "275" in all_content: state["stew_calories_correct"] = True
        if "6.70" in all_content or "6.7" in all_content: state["sliders_cost_correct"] = True
        if "600" in all_content: state["sliders_calories_correct"] = True

    # Check for skill usage in trace (mocked logic here for state)
    if os.path.exists("trace.jsonl"):
        with open("trace.jsonl", "r") as f:
            trace = f.read()
            if "heritage_recipe_decoder" in trace:
                state["skill_used_heritage"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
