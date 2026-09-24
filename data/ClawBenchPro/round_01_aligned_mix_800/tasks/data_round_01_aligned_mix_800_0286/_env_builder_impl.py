import os
import csv

def build_env():
    # 1. Create directories
    os.makedirs("volunteer_signups", exist_ok=True)
    os.makedirs("student_data", exist_ok=True)

    # 2. Generate volunteer signups (Some will be cleared by API, some not)
    week1_data = [
        ["Name", "Role", "Phone"],
        ["Maria Silva", "Stage Hand", "555-0101"],
        ["Bob Builder", "Snacks", "555-0102"], # Uncleared
        ["Sarah Jenkins", "Usher", "555-0103"]
    ]
    with open("volunteer_signups/week1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(week1_data)

    week2_data = [
        ["Name", "Role", "Phone"],
        ["Carlos Mendes", "Audio", "555-0104"],
        ["Karen Smith", "Decorations", "555-0105"], # Uncleared
        ["Lucia Santos", "Costumes", "555-0106"]
    ]
    with open("volunteer_signups/week2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(week2_data)

    # Note: security/cleared_backgrounds.txt is removed. Agent must use API skills.
    
    # 3. Generate Student Requests
    # Valid: Leo, Sam, Ana. Invalid (needs consultation): Mia, David, Omar.
    # Note: iep_accessibility.json is removed. Agent must use Evaluator skill.
    student_requests = [
        ["Student_Name", "IEP_Motor_Level", "Requested_Instrument"],
        ["Leo", "Motor_Level_1", "Tambourine"],
        ["Mia", "Motor_Level_1", "Guitar"], # Invalid
        ["Sam", "Motor_Level_2", "Keyboard"],
        ["David", "Motor_Level_2", "Drums"], # Invalid
        ["Ana", "Motor_Level_3", "Flute"],
        ["Omar", "Motor_Level_3", "Triangle"] # Invalid
    ]
    with open("student_data/requests.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(student_requests)

if __name__ == "__main__":
    build_env()
