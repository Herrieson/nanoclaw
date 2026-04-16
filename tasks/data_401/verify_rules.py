import os
import json
import re

def verify():
    base_dir = "."
    estimate_file = os.path.join(base_dir, "final_estimate.txt")
    
    state = {
        "file_exists": False,
        "content": "",
        "extracted_area": None,
        "extracted_cost": None,
        "selected_concrete": None,
        "selected_lumber": None,
        "selected_steel": None,
        "expected_area": 1168,
        "expected_concrete_supplier": "Cemex Mex",
        "expected_lumber_supplier": "WoodWorks",
        "expected_steel_supplier": "US Steel Co",
        "expected_total_cost": 15534.40 # 1168 * (4.00 + 3.50 + 5.80) = 1168 * 13.30 = 15534.4
    }

    if os.path.exists(estimate_file):
        state["file_exists"] = True
        with open(estimate_file, "r", encoding="utf-8") as f:
            content = f.read()
            state["content"] = content

        # Try to extract numbers
        numbers = re.findall(r"\d+(?:\.\d+)?", content)
        if numbers:
            # We don't know exactly how the agent formatted it, so we pass the raw content and some extracted numbers to the LLM judge
            pass
            
        # Try to heuristically check for suppliers in the text
        lower_content = content.lower()
        if "cemex mex" in lower_content:
            state["selected_concrete"] = "Cemex Mex"
        if "woodworks" in lower_content:
            state["selected_lumber"] = "WoodWorks"
        if "us steel co" in lower_content:
            state["selected_steel"] = "US Steel Co"

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
