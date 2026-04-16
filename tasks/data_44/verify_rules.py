import os
import csv
import json

def verify():
    base_dir = "."
    csv_file = os.path.join(base_dir, "urgent_patients.csv")
    txt_file = os.path.join(base_dir, "summary.txt")
    
    state = {
        "csv_exists": False,
        "txt_exists": False,
        "csv_headers_correct": False,
        "urgent_patients_found": [],
        "total_urgent_correct": False,
        "summary_number": None,
        "false_positives": []
    }
    
    expected_urgent = {"Bob Johnson", "Charlie Nguyen", "Diana Prince", "Hannah Abbott", "Jane Doe"}
    
    if os.path.exists(csv_file):
        state["csv_exists"] = True
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and "Name" in headers and "Age" in headers and "Phone" in headers:
                    state["csv_headers_correct"] = True
                
                found_names = []
                for row in reader:
                    name = row.get("Name", "").strip()
                    found_names.append(name)
                    if name in expected_urgent:
                        state["urgent_patients_found"].append(name)
                    else:
                        state["false_positives"].append(name)
        except Exception as e:
            pass
            
    if os.path.exists(txt_file):
        state["txt_exists"] = True
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                state["summary_number"] = content
                if content == str(len(expected_urgent)):
                    state["total_urgent_correct"] = True
        except Exception:
            pass

    state["urgent_patients_found"] = list(set(state["urgent_patients_found"]))
    
    with open(os.path.join(base_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
