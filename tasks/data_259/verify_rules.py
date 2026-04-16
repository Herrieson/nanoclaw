import os
import json

def verify():
    base_dir = "."
    org_dir = os.path.join(base_dir, "organized_records")
    
    state = {
        "organized_records_exists": False,
        "all_students_processed": False,
        "json_formats_correct": False,
        "project_contents_correct": False,
        "errors": []
    }
    
    if not os.path.exists(org_dir):
        state["errors"].append("The 'organized_records' directory was not created.")
        return state
        
    state["organized_records_exists"] = True
    
    students = {
        "Alice Smith": {"Math": "95", "Science": "88", "English": "92", "ProjectID": "PRJ-101", "content": "Alice wrote about the solar system."},
        "Bob Jones": {"Math": "78", "Science": "85", "English": "80", "ProjectID": "PRJ-102", "content": "Bob's project is about local ecosystems."},
        "Charlie Brown": {"Math": "88", "Science": "90", "English": "85", "ProjectID": "PRJ-103", "content": "Charlie created a volcano model report."},
        "Diana Prince": {"Math": "100", "Science": "98", "English": "99", "ProjectID": "PRJ-104", "content": "Diana studied the history of ancient Greece."}
    }
    
    students_processed = 0
    json_correct = 0
    projects_correct = 0
    
    for student, expected in students.items():
        student_dir = os.path.join(org_dir, student)
        if not os.path.exists(student_dir):
            state["errors"].append(f"Directory for student '{student}' is missing.")
            continue
            
        students_processed += 1
        
        # Check JSON
        json_path = os.path.join(student_dir, "grades.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    # Allow integers or strings, but strip spaces if strings
                    math_val = str(data.get("Math")).strip()
                    sci_val = str(data.get("Science")).strip()
                    eng_val = str(data.get("English")).strip()
                    pid_val = str(data.get("ProjectID")).strip()
                    
                    if math_val == expected["Math"] and sci_val == expected["Science"] and eng_val == expected["English"] and pid_val == expected["ProjectID"]:
                        json_correct += 1
                    else:
                        state["errors"].append(f"Data mismatch in grades.json for {student}. Expected Math {expected['Math']}, Sci {expected['Science']}, Eng {expected['English']}, PID {expected['ProjectID']}. Got: {data}")
            except Exception as e:
                state["errors"].append(f"Failed to parse grades.json for {student}: {str(e)}")
        else:
            state["errors"].append(f"grades.json missing for {student}")
            
        # Check Project Summary
        proj_path = os.path.join(student_dir, "project_summary.txt")
        if os.path.exists(proj_path):
            with open(proj_path, 'r') as f:
                content = f.read().strip()
                if content == expected["content"]:
                    projects_correct += 1
                else:
                    state["errors"].append(f"Project content mismatch for {student}.")
        else:
            state["errors"].append(f"project_summary.txt missing for {student}")

    if students_processed == len(students):
        state["all_students_processed"] = True
    if json_correct == len(students):
        state["json_formats_correct"] = True
    if projects_correct == len(students):
        state["project_contents_correct"] = True
        
    return state

if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2))
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)
