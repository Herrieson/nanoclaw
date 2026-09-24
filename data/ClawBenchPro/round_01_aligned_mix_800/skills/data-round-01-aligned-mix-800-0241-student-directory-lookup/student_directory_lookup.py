import sys
import json

def lookup_student(student_id):
    # Mock school database
    database = {
        "STU-101": {"name": "Ethan Miller", "grade": 10},
        "STU-102": {"name": "Chloe Chen", "grade": 11},
        "STU-103": {"name": "Marcus Thorne", "grade": 10},
        "STU-104": {"name": "Sarah Jenkins", "grade": 9},
        "STU-105": {"name": "Leo Rodriguez", "grade": 12}
    }
    
    student_id = student_id.strip().upper()
    if student_id in database:
        return json.dumps(database[student_id])
    else:
        return json.dumps({"error": "Student ID not found in directory."})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing STUDENT_ID. Usage: python student_directory_lookup.py <STUDENT_ID>"}))
    else:
        print(lookup_student(sys.argv[1]))
