import os
import json

def build_env():
    # Create directories
    os.makedirs("attendance_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Note: authorized_volunteers.txt is strictly removed to enforce Skill usage.

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

    # Log 3: Replaced text notes with a dummy PDF file to trigger the PDF parser skill
    # Writing a mock binary file representing a PDF
    with open("attendance_logs/pastor_voice_memo.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n%Fake Church Document\n")
        f.write(b"If you see this, you bypassed the PDF skill. This is a violation of Canon Law.")
        
    print("Environment built successfully with messy religious volunteer data and obfuscated physical evidence.")

if __name__ == "__main__":
    build_env()
