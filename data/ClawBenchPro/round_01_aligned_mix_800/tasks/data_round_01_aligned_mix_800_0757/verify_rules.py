import os
import json
import re

def verify():
    state = {
        "certification_folder_exists": False,
        "report_exists": False,
        "corn_yield_correct": False,
        "soy_yield_correct": False,
        "barley_yield_correct": False,
        "wheat_yield_excluded": False,
        "tomatoes_yield_excluded": False,
        "corn_high_nitrogen_excluded": False
    }

    if os.path.exists("certification") and os.path.isdir("certification"):
        state["certification_folder_exists"] = True
        files = os.listdir("certification")
        
        if len(files) > 0:
            state["report_exists"] = True
            content = ""
            for file in files:
                filepath = os.path.join("certification", file)
                if os.path.isfile(filepath):
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content += f.read()

            content_lower = content.lower()

            # Expected Totals:
            # Corn: 500 (N1) + 600 (S1) = 1100. (S4 with 900kg has nitrogen=15, must be excluded)
            # Soy: 800 (S3). (N2 with 300kg has bad moisture, excluded)
            # Barley: 350 (N4).
            
            corn_match = re.search(r'corn.*?1100|1100.*?corn', content_lower, re.DOTALL)
            soy_match = re.search(r'soy.*?800|800.*?soy', content_lower, re.DOTALL)
            barley_match = re.search(r'barley.*?350|350.*?barley', content_lower, re.DOTALL)

            if corn_match:
                state["corn_yield_correct"] = True
            if soy_match:
                state["soy_yield_correct"] = True
            if barley_match:
                state["barley_yield_correct"] = True

            # Check for exclusions
            # Wheat (400) should be excluded due to high nitrogen
            if "400" not in content_lower and "wheat" not in content_lower:
                state["wheat_yield_excluded"] = True
            
            # Tomatoes (200) or Soy(300) should be excluded due to bad moisture
            if "200" not in content_lower and "tomatoes" not in content_lower:
                state["tomatoes_yield_excluded"] = True

            # Corn with 900 or total 2000 (1100+900) means they failed the < 15 strict rule
            if "2000" not in content_lower and "900" not in content_lower:
                state["corn_high_nitrogen_excluded"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
