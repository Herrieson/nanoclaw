import os
import json
import sys

def verify():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(base_dir, "deliverables")
    
    state = {
        "deliverables_folder_exists": os.path.isdir(deliverables_dir),
        "output_file_exists": False,
        "found_top_1": False,
        "found_top_2": False,
        "found_top_3": False,
        "found_invalid_data": False,
        "found_runner_up": False
    }

    if state["deliverables_folder_exists"]:
        files = os.listdir(deliverables_dir)
        if files:
            state["output_file_exists"] = True
            content = ""
            for f in files:
                file_path = os.path.join(deliverables_dir, f)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content += file.read()
                    except Exception:
                        pass
            
            content_upper = content.upper()
            
            # The top 3 valid subjects are SUBJ_005, SUBJ_002, SUBJ_010(wait no, SUBJ_009 is valid, MEQ 13.33)
            # Let's list valid MEQs:
            # 005: 20.625 (Top 1)
            # 002: 16.666 (Top 2)
            # 009: 13.333 (Top 3)
            # 006: 10.888 (Rank 4)
            
            if "SUBJ_005" in content_upper:
                state["found_top_1"] = True
            if "SUBJ_002" in content_upper:
                state["found_top_2"] = True
            if "SUBJ_009" in content_upper:
                state["found_top_3"] = True
                
            # Check if they included invalid ones
            invalid_subjects = ["SUBJ_004", "SUBJ_007", "SUBJ_008", "SUBJ_010"]
            for inv in invalid_subjects:
                if inv in content_upper:
                    state["found_invalid_data"] = True
                    
            if "SUBJ_006" in content_upper:
                state["found_runner_up"] = True

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == '__main__':
    verify()
