import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "report_file_exists": False,
        "found_megacorp": False,
        "found_global_retailers": False,
        "found_correct_hours": False
    }

    deliverables_path = "deliverables"
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        files = os.listdir(deliverables_path)
        if len(files) > 0:
            state["report_file_exists"] = True
            
            # Read all files in the directory to find the data
            report_content = ""
            for file_name in files:
                file_path = os.path.join(deliverables_path, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            report_content += f.read().lower()
                    except:
                        pass
            
            # Check for the flaky businesses
            if "megacorp oil" in report_content or "megacorp" in report_content:
                state["found_megacorp"] = True
            if "global retailers" in report_content or "global retailers llc" in report_content:
                state["found_global_retailers"] = True
                
            # Check for exactly 48 or 48.0 hours
            if "48" in report_content or "48.0" in report_content:
                state["found_correct_hours"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    # If a workspace path is provided, change to it
    import sys
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])
    verify()
