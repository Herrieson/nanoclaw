import os
import csv
import json

def build_env():
    # 创建目录
    os.makedirs("service_logs", exist_ok=True)
    os.makedirs("registry", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 创建白名单
    certified_staff = [
        {"id": "V-101", "name": "Nguyen Lan", "role": "Senior Aide"},
        {"id": "V-102", "name": "Tran Minh", "role": "Personal Care Aide"},
        {"id": "V-105", "name": "Pham Huong", "role": "Home Support"}
    ]
    with open("registry/certified_staff.csv", "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "role"])
        writer.writeheader()
        writer.writerows(certified_staff)

    # 2. 创建服务日志 (包含干扰项和脏数据)
    # 文件1: 格式良好的合法记录
    log1 = [
        {"staff_id": "V-101", "duration_mins": 120, "date": "2023-10-01"},
        {"staff_id": "V-101", "duration_mins": 90, "date": "2023-10-02"}
    ]
    with open("service_logs/monday_report.json", "w") as f:
        json.dump(log1, f)

    # 文件2: 包含非法人员和混乱格式的txt
    log2 = "staff_id:V-102,duration_mins:180,date:2023-10-01\nstaff_id:X-999,duration_mins:300,date:2023-10-01"
    with open("service_logs/tuesday_raw.txt", "w") as f:
        f.write(log2)

    # 文件3: 只有非法人员
    log3 = [{"staff_id": "X-888", "duration_mins": 60, "date": "2023-10-03"}]
    with open("service_logs/wednesday.json", "w") as f:
        json.dump(log3, f)

    # 文件4: 合法人且带一点脏数据（空行/坏值）
    with open("service_logs/thursday_notes.csv", "w") as f:
        f.write("staff_id,duration_mins,date\n")
        f.write("V-105,150,2023-10-04\n")
        f.write(",,\n") # 空行
        f.write("V-105,not_a_number,2023-10-04\n") # 坏数据

if __name__ == "__main__":
    build_env()
