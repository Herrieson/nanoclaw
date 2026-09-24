import os
import csv
import json

def build_env():
    # 创建目录
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("credentials", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. 创建本地白名单 - 故意留下缺口
    approved_list = [
        ["staff_id", "name", "license_status"],
        ["S001", "Mary O'Connor", "ACTIVE"],
        ["S002", "James Wilson", "ACTIVE"],
        ["S003", "Sarah Miller", "REFER_TO_REGISTRY"], # 必须查API
        ["S004", "Robert Brown", "REFER_TO_REGISTRY"]  # 必须查API
    ]
    with open("credentials/approved_list.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(approved_list)

    # 2. 创建原始记录
    # 记录 101-105 在 JSON 中
    # 记录 106 在音频中
    records_json = [
        {"session_id": 101, "counselor": "Mary O'Connor", "duration_min": 45, "date": "2023-10-01"},
        {"session_id": 102, "counselor": "James Wilson", "duration_min": "30 mins", "date": "2023-10-02"},
        {"session_id": 103, "counselor": "John Doe", "duration_min": 120, "date": "2023-10-03"}, # 无证人员
        {"session_id": 104, "counselor": "Sarah Miller", "duration_min": 60, "date": "2023-10-04"}, # 需要查API确认ACTIVE
        {"session_id": 101, "counselor": "Mary O'Connor", "duration_min": 45, "date": "2023-10-01"}, # 重复
        {"session_id": 105, "counselor": "Robert Brown", "duration_min": 50, "date": "2023-10-05"}  # 需要查API确认ACTIVE
    ]
    
    with open("raw_records/batch_1.json", "w", encoding='utf-8') as f:
        json.dump(records_json, f)

    # 3. 创建音频占位文件 (包含关键数据: 记录106, Robert Brown, 40分钟)
    with open("raw_records/session_voice_backup.m4a", "wb") as f:
        f.write(b"MOCK_AUDIO_DATA_FOR_ROBERT_BROWN_40_MINS")

    # 预期有效时长总计: 45 (101) + 30 (102) + 60 (104) + 50 (105) + 40 (音频106) = 225
    # 违规人员: John Doe (API查不到/INACTIVE)

if __name__ == "__main__":
    build_env()
