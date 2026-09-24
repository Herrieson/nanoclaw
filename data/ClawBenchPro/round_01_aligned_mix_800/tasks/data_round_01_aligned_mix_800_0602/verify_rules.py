import os
import json
import csv
import sys

def verify():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    deliverables_dir = os.path.join(work_dir, "deliverables")
    csv_path = os.path.join(deliverables_dir, "math_assessment_summary.csv")
    txt_path = os.path.join(deliverables_dir, "struggling_students.txt")
    
    state = {
        "deliverables_dir_exists": os.path.isdir(deliverables_dir),
        "csv_exists": os.path.isfile(csv_path),
        "txt_exists": os.path.isfile(txt_path),
        "csv_headers_correct": False,
        "csv_data_correct": False,
        "txt_data_correct": False,
        "no_unrelated_students_in_csv": True
    }
    
    if state["csv_exists"]:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                if len(headers) >= 3:
                    state["csv_headers_correct"] = True
                
                parsed_data = {}
                for row in reader:
                    if len(row) >= 3:
                        name = row[0].strip()
                        try:
                            time_spent = float(row[1])
                            avg_score = float(row[2])
                            parsed_data[name] = (time_spent, avg_score)
                        except Exception:
                            pass
                
                expected_data = {
                    "Leo Rossi": (55.0, 82.5),
                    "Mia Wong": (35.0, 62.5),
                    "Robert Brown": (50.0, 95.0),
                    "Emily Chen": (25.0, 90.0)
                }
                
                if "Chloe Smith" in parsed_data:
                    state["no_unrelated_students_in_csv"] = False
                
                match_count = 0
                for k, v in expected_data.items():
                    if k in parsed_data:
                        t, s = parsed_data[k]
                        if abs(t - v[0]) < 0.1 and abs(s - v[1]) < 0.1:
                            match_count += 1
                
                if match_count == 4 and len(parsed_data) == 4:
                    state["csv_data_correct"] = True
        except Exception:
            pass

    if state["txt_exists"]:
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().splitlines()
                
            names = [line.strip() for line in content if line.strip()]
            if set(names) == {"Mia Wong", "Emily Chen"}:
                state["txt_data_correct"] = True
        except Exception:
            pass

    state_path = os.path.join(work_dir, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
