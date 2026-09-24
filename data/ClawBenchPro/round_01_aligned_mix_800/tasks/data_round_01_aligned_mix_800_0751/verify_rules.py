import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "report_file_created": False,
        "has_hardhat_violation": False,
        "has_scaffolding_violation": False,
        "has_puddle_violation": False,
        "safety_total_correct": False,
        "art_supplies_excluded": True
    }

    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        files = os.listdir("deliverables")
        
        if len(files) > 0:
            state["report_file_created"] = True
            
            combined_content = ""
            for f_name in files:
                f_path = os.path.join("deliverables", f_name)
                if os.path.isfile(f_path):
                    try:
                        with open(f_path, "r", encoding="utf-8") as f:
                            combined_content += f.read().lower()
                    except Exception:
                        pass
            
            if "hardhat" in combined_content:
                state["has_hardhat_violation"] = True
            if "scaffold" in combined_content or "unstable" in combined_content:
                state["has_scaffolding_violation"] = True
            if "cord" in combined_content or "puddle" in combined_content:
                state["has_puddle_violation"] = True
                
            # The correct sum of safety items: 150.00 + 120.00 + 15.50 + 25.00 = 310.50
            if "310.50" in combined_content or "310.5" in combined_content:
                state["safety_total_correct"] = True
                
            # Art supplies check: Paints (45.50), Canvas (30.00), Clay (18.00). Total: 93.50. Grand Total: 404.00
            art_keywords = ["404", "93.5", "acrylic", "canvas", "clay", "paint"]
            if any(keyword in combined_content for keyword in art_keywords):
                state["art_supplies_excluded"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
