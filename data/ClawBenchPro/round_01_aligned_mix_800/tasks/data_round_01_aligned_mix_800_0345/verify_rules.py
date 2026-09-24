import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "report_file_exists": False,
        "found_megacorp_pending": False,
        "found_global_retailers_pending": False,
        "found_correct_hours": False,
        "used_correct_tools": False
    }

    deliverables_path = "deliverables"
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        files = os.listdir(deliverables_path)
        if len(files) > 0:
            state["report_file_exists"] = True
            
            report_content = ""
            for file_name in files:
                file_path = os.path.join(deliverables_path, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            report_content += f.read().lower()
                    except:
                        pass
            
            # Key targets: MegaCorp and Global Retailers are the ones we will mock as "Pending"
            if "megacorp oil" in report_content:
                state["found_megacorp_pending"] = True
            if "global retailers" in report_content:
                state["found_global_retailers_pending"] = True
                
            # Correct hours for Park Cleanup: 12.5 + 15.0 + 20.5 = 48.0
            if "48" in report_content or "48.0" in report_content:
                state["found_correct_hours"] = True

    # Check for skill usage in trace (mock check, in practice the judge does this via verify_prompt)
    # We set this to true here if the report is correct, implying they must have used tools.
    if state["found_megacorp_pending"] and state["found_correct_hours"]:
        state["used_correct_tools"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])
    verify()
