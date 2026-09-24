import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "report_file_created": False,
        "ocr_used_for_hardhat": False,
        "has_scaffolding_violation": False,
        "has_puddle_violation": False,
        "safety_total_correct": False,
        "api_queried": False
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
                    with open(f_path, "r", encoding="utf-8", errors='ignore') as f:
                        combined_content += f.read().lower()
            
            # Monday violation (only in the photo/OCR)
            if "hardhat" in combined_content or "zone b" in combined_content:
                state["ocr_used_for_hardhat"] = True
            
            # Wednesday violations
            if "scaffold" in combined_content or "unstable" in combined_content:
                state["has_scaffolding_violation"] = True
            if "cord" in combined_content or "puddle" in combined_content:
                state["has_puddle_violation"] = True
                
            # Calculation: 150.00 + 120.00 + 15.50 + 25.00 = 310.50
            if "310.50" in combined_content or "310.5" in combined_content:
                state["safety_total_correct"] = True

    # Note: api_queried would typically be checked in trace.jsonl, 
    # but for state we check if the agent reached the correct number which implies API usage.
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
