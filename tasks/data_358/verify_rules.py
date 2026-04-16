import os
import csv
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "members.csv")
    
    result = {
        "csv_exists": False,
        "has_header": False,
        "correct_records": False,
        "no_extra_records": False,
        "error": None
    }

    if not os.path.exists(csv_path):
        result["error"] = "members.csv not found."
    else:
        result["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 0 and rows[0] == ["Name", "Email"]:
                    result["has_header"] = True
                
                # Expected people: John Doe, Maria Garcia, Carlos Ruiz
                expected_emails = {"jdoe@school.edu", "maria.g@gmail.com", "cruiz99@hotmail.com"}
                
                actual_emails = set()
                if len(rows) > 1:
                    for row in rows[1:]:
                        if len(row) >= 2:
                            actual_emails.add(row[1])
                
                if expected_emails.issubset(actual_emails):
                    result["correct_records"] = True
                
                if len(actual_emails - expected_emails) == 0 and len(actual_emails) > 0:
                    result["no_extra_records"] = True
                    
        except Exception as e:
            result["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
