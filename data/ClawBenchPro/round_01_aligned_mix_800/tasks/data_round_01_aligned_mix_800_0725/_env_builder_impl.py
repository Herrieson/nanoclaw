import os
import json

def build_env():
    # Create directories
    os.makedirs("attendance_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Authorized Volunteers List
    authorized = [
        "Mary Sobieski",
        "John Kowalski",
        "Agnieszka Novak",
        "Robert Miller",
        "Theresa Wisniewski"
    ]
    with open("authorized_volunteers.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(authorized))

    # 2. Raw logs with messy data
    # Log 1: Time range
    with open("attendance_logs/week1.csv", "w", encoding="utf-8") as f:
        f.write("Volunteer,Time_Spent\n")
        f.write("Mary Sobieski,3.5 hours\n")
        f.write("John Kowalski,120 min\n")
        f.write("Intruder Dave,60 min\n") # Unauthorized

    # Log 2: More messy data
    with open("attendance_logs/week2.json", "w", encoding="utf-8") as f:
        logs = [
            {"name": "Mary Sobieski", "duration": "09:00-11:30"}, # 2.5h
            {"name": "Agnieszka Novak", "duration": "4 hours"},
            {"name": "Evil Steve", "duration": "30 min"} # Unauthorized
        ]
        json.dump(logs, f)

    # Log 3: Additional entries
    with open("attendance_logs/notes.txt", "w", encoding="utf-8") as f:
        f.write("Robert Miller worked for 5.2 hours on Sunday.\n")
        f.write("Theresa Wisniewski stayed from 13:00 to 14:15.\n") # 1.25h
        f.write("Mary Sobieski added another 1 hour of prep.\n")

    print("Environment built successfully with messy religious volunteer data.")

if __name__ == "__main__":
    build_env()
