import os
import csv
import json

def build_env():
    # 创建目录
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("credentials", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. 创建白名单 (Approved List)
    approved_list = [
        ["staff_id", "name", "license_type"],
        ["S001", "Mary O'Connor", "LPC"],
        ["S002", "James Wilson", "LCSW"],
        ["S003", "Sarah Miller", "PhD"],
        ["S004", "Robert Brown", "LPC"]
    ]
    with open("credentials/approved_list.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(approved_list)

    # 2. 创建原始记录（脏数据、重复项、格式不一）
    # 预期有效时长: 45 + 30 + 60 + 50 = 185
    # 违规人员: "John Doe" (不在名单)
    records = [
        {"session_id": 101, "counselor": "Mary O'Connor", "duration_min": 45, "date": "2023-10-01"},
        {"session_id": 102, "counselor": "James Wilson", "duration_min": "30 mins", "date": "2023-10-02"}, # 格式不一
        {"session_id": 103, "counselor": "John Doe", "duration_min": 120, "date": "2023-10-03"}, # 违规
        {"session_id": 104, "counselor": "Sarah Miller", "duration_min": 60, "date": "2023-10-04"},
        {"session_id": 101, "counselor": "Mary O'Connor", "duration_min": 45, "date": "2023-10-01"}, # 重复项
        {"session_id": 105, "counselor": "Robert Brown", "duration_min": 50, "date": "2023-10-05"}
    ]
    
    # 分散存储到多个 JSON 文件中以增加难度
    with open("raw_records/batch_1.json", "w", encoding='utf-8') as f:
        json.dump(records[:3], f)
    with open("raw_records/batch_2.json", "w", encoding='utf-8') as f:
        json.dump(records[3:], f)

    # 添加一个干扰文件
    with open("raw_records/readme.txt", "w") as f:
        f.write("Handle these files with care. The director is very sensitive about data privacy.")

if __name__ == "__main__":
    build_env()
