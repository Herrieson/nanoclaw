import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("case_files", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)

    # 1. 创建授权名单
    authorized_staff = ["Siobhan O'Sullivan", "Liam Murphy", "Aisling Quinn"]
    with open("case_files/authorized_staff.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(authorized_staff))

    # 2. 创建脏数据访问日志 (包含干扰项和需要计算的数据)
    # 字段：timestamp, user, duration_minutes, action
    access_logs = [
        {"ts": "2024-05-01 09:00", "user": "Siobhan O'Sullivan", "duration": 120, "action": "File Review"},
        {"ts": "2024-05-01 11:30", "user": "John Doe", "duration": 15, "action": "Unauthorized Copy"}, # 违规
        {"ts": "2024-05-02 10:00", "user": "Liam Murphy", "duration": 45, "action": "Drafting"},
        {"ts": "2024-05-02 14:00", "user": "Aisling Quinn", "duration": 30, "action": "Evidence Tagging"},
        {"ts": "2024-05-03 16:00", "user": "Jane Smith", "duration": 10, "action": "File Browsing"}, # 违规
        {"ts": "2024-05-03 17:00", "user": "Siobhan O'Sullivan", "duration": 200, "action": "Brief Writing"},
        {"ts": "2024-05-04 08:30", "user": "Liam Murphy", "duration": 60, "action": "Consultation"}
    ]
    
    # 以 CSV 格式增加难度，混入一些多余的空格
    with open("case_files/access_logs.csv", "w", encoding="utf-8") as f:
        f.write("timestamp,user_name,duration_min,activity\n")
        for entry in access_logs:
            f.write(f"{entry['ts']}, {entry['user']} ,{entry['duration']},{entry['action']}\n")

    # 3. 干扰文件
    with open("case_files/notes.tmp", "w") as f:
        f.write("Don't forget to buy more coffee beans.")

if __name__ == "__main__":
    build_env()
