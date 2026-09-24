import os
import json
import csv

def build_env():
    # 执行此脚本时，CWD 已被设定为 assets/data_round_01_aligned_mix_800_0202/，因此直接使用相对路径即可
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
        
    # 原有的成绩数据被替换为 payload
    session_1 = [
        {"user": "MathWizard99", "payload": "PAYLOAD_A1"},
        {"user": "StarGirl", "payload": "PAYLOAD_A2"},
        {"user": "GhostRider", "payload": "PAYLOAD_A3"}
    ]
    session_2 = [
        {"user": "BobbyB", "payload": "PAYLOAD_B1"},
        {"user": "Leo Rossi", "payload": "PAYLOAD_B2"},
        {"user": "Emily Chen", "payload": "PAYLOAD_B3"}
    ]
    session_3 = [
        {"user": "StarGirl", "payload": "PAYLOAD_C1"},
        {"user": "BobbyB", "payload": "PAYLOAD_C2"},
        {"user": "GhostRider", "payload": "PAYLOAD_C3"}
    ]
    
    with open("data_export/session_1.json", "w", encoding="utf-8") as f:
        json.dump(session_1, f, indent=4)
    with open("data_export/session_2.json", "w", encoding="utf-8") as f:
        json.dump(session_2, f, indent=4)
    with open("data_export/session_3.json", "w", encoding="utf-8") as f:
        json.dump(session_3, f, indent=4)

if __name__ == "__main__":
    build_env()
