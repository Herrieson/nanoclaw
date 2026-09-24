import os
import json
import glob

def verify():
    state = {
        "green_report_dir_exists": False,
        "json_file_exists": False,
        "valid_json_format": False,
        "extracted_report_data": None
    }

    # 1. Check if directory exists
    if os.path.exists("green_report") and os.path.isdir("green_report"):
        state["green_report_dir_exists"] = True
        
        # 2. Check if a JSON file exists in the directory
        json_files = glob.glob("green_report/*.json")
        if json_files:
            state["json_file_exists"] = True
            
            # 3. Try to parse the JSON file and extract data
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    state["valid_json_format"] = True
                    state["extracted_report_data"] = data
            except Exception as e:
                state["extracted_report_data"] = f"Error parsing JSON: {str(e)}"

    # 4. Write the objective facts to state.json for the LLM judge
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
