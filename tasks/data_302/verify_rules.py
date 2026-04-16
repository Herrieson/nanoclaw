import os
import json
import sqlite3

def verify():
    workspace = "."
    json_path = os.path.join(workspace, "optimal_yoga.json")
    db_path = os.path.join(workspace, "employees.db")
    
    expected_schedule = {
        "Monday": "13:00",
        "Tuesday": "13:30",
        "Wednesday": "13:30",
        "Thursday": "12:00",
        "Friday": "12:00"
    }
    
    result = {
        "json_exists": False,
        "json_correct": False,
        "db_updated": False,
        "db_correct": False,
        "details": ""
    }
    
    if os.path.exists(json_path):
        result["json_exists"] = True
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            if data == expected_schedule:
                result["json_correct"] = True
            else:
                result["details"] += f"JSON content mismatch. Got {data}. "
        except Exception as e:
            result["details"] += f"Failed to parse JSON: {e}. "
            
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT day, start_time FROM wellness_schedule")
            rows = c.fetchall()
            result["db_updated"] = True
            db_schedule = {row[0]: row[1] for row in rows}
            if db_schedule == expected_schedule:
                result["db_correct"] = True
            else:
                result["details"] += f"DB content mismatch. Got {db_schedule}. "
        except Exception as e:
            result["details"] += f"Failed to verify DB: {e}. "

    score = 0
    if result["json_correct"]:
        score += 50
    if result["db_correct"]:
        score += 50

    result["score"] = score

    with open(os.path.join(workspace, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
