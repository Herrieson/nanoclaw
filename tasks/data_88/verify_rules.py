import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "final_upload.csv")
    
    state = {
        "file_exists": False,
        "format_correct": False,
        "david_points": None,
        "maria_points": None,
        "david_correct": False,
        "maria_correct": False
    }
    
    if os.path.exists(csv_path):
        state["file_exists"] = True
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                parsed_data = {}
                for row in reader:
                    if len(row) == 2:
                        parsed_data[row[0].strip()] = float(row[1].strip())
                
                if parsed_data:
                    state["format_correct"] = True
                
                # Check David
                if "DAVID S." in parsed_data:
                    state["david_points"] = parsed_data["DAVID S."]
                    if abs(parsed_data["DAVID S."] - 47.0) < 0.1:
                        state["david_correct"] = True
                
                # Check Maria
                if "MARIA G." in parsed_data:
                    state["maria_points"] = parsed_data["MARIA G."]
                    if abs(parsed_data["MARIA G."] - 50.0) < 0.1:
                        state["maria_correct"] = True
                        
        except Exception as e:
            state["error"] = str(e)
            
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)
        
if __name__ == "__main__":
    verify()
