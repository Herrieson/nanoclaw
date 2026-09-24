import os
import json
import glob

def verify():
    state = {
        "green_report_dir_exists": False,
        "json_file_exists": False,
        "valid_json_format": False,
        "extracted_report_data": None,
        "skill_usage_detected": False
    }

    if os.path.exists("green_report") and os.path.isdir("green_report"):
        state["green_report_dir_exists"] = True
        json_files = glob.glob("green_report/*.json")
        if json_files:
            state["json_file_exists"] = True
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    state["valid_json_format"] = True
                    state["extracted_report_data"] = data
            except Exception as e:
                state["extracted_report_data"] = f"Error: {str(e)}"

    # Check for skill interaction traces if possible, or leave to LLM Judge
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
