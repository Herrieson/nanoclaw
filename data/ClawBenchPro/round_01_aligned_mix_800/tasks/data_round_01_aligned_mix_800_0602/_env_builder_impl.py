import os
import json
import csv

def build_env():
    # 执行此脚本时，CWD 已被设定为 assets/data_round_01_aligned_mix_800_0602/，因此直接使用相对路径即可
    os.makedirs("data_export", exist_ok=True)
    
    roster = [
        {"student_id": "101", "official_name": "Leo Rossi", "grade": 5},
        {"student_id": "102", "official_name": "Mia Wong", "grade": 5},
        {"student_id": "103", "official_name": "Robert Brown", "grade": 5},
        {"student_id": "104", "official_name": "Emily Chen", "grade": 5},
        {"student_id": "105", "official_name": "Chloe Smith", "grade": 5}
    ]
    with open("data_export/class_roster.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_id", "official_name", "grade"])
        writer.writeheader()
        writer.writerows(roster)
        
    aliases = {
        "MathWizard99": "Leo Rossi",
        "StarGirl": "Mia Wong",
        "BobbyB": "Robert Brown",
        "GhostRider": "Chloe Smith"
    }
    with open("data_export/aliases.json", "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=4)
        
    session_1 = [
        {"user": "MathWizard99", "module": "math", "time_spent_min": 45, "score": 85},
        {"user": "StarGirl", "module": "math", "time_spent_min": 20, "score": 60},
        {"user": "GhostRider", "module": "reading", "time_spent_min": 40, "score": 100}
    ]
    session_2 = [
        {"user": "BobbyB", "module": "reading", "time_spent_min": 30, "score": 90},
        {"user": "Leo Rossi", "module": "math", "time_spent_min": 10, "score": 80},
        {"user": "Emily Chen", "module": "math", "time_spent_min": 25, "score": 90}
    ]
    session_3 = [
        {"user": "StarGirl", "module": "math", "time_spent_min": 15, "score": 65},
        {"user": "BobbyB", "module": "math", "time_spent_min": 50, "score": 95},
        {"user": "GhostRider", "module": "science", "time_spent_min": 20, "score": 88}
    ]
    
    with open("data_export/session_1.json", "w", encoding="utf-8") as f:
        json.dump(session_1, f, indent=4)
    with open("data_export/session_2.json", "w", encoding="utf-8") as f:
        json.dump(session_2, f, indent=4)
    with open("data_export/session_3.json", "w", encoding="utf-8") as f:
        json.dump(session_3, f, indent=4)

if __name__ == "__main__":
    build_env()
