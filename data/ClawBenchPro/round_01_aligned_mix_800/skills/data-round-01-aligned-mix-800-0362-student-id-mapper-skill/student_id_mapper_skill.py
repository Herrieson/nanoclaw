import sys
import json

def run(name, grade):
    # Mock Database
    db = {
        "Leo": "SID-8821", "Mia": "SID-1029", "Zoe": "SID-4492",
        "Carlos": "SID-3301", "Sam": "SID-9920", "Alex": "SID-5512",
        "Chloe": "SID-2210", "Emma": "SID-7731"
    }
    student_id = db.get(name, "SID-0000")
    return json.dumps({"name": name, "student_id": student_id, "status": "Active"})

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(run(sys.argv[1], sys.argv[2]))
