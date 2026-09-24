import os
import json

def verify():
    state = {
        "pta_report_dir_exists": False,
        "report_file_exists": False,
        "correct_total_growth_found": False,
        "missing_students_identified": False,
        "used_correct_skill": False
    }
    
    # Check output
    report_dir = "pta_report"
    if os.path.isdir(report_dir):
        state["pta_report_dir_exists"] = True
        files = os.listdir(report_dir)
        if files:
            state["report_file_exists"] = True
            for file_name in files:
                file_path = os.path.join(report_dir, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            # Total Native: Alice(3.5) + Bob(4.0) + Daisy(2.0) + Hannah(5.5) = 15.0
                            if "15.0" in content or "15 inches" in content:
                                state["correct_total_growth_found"] = True
                            
                            # Missing: Ethan, Fiona
                            if "ethan" in content and "fiona" in content:
                                state["missing_students_identified"] = True
                    except:
                        pass

    # Note: 'used_correct_skill' will be evaluated by the LLM Judge from the trace.
    # We write state.json for the objective part.
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
