import os
import json
import base64

def build_env():
    # 创建目录结构
    os.makedirs("case_files", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)

    # 创建需要计算的数据
    # 字段：timestamp, user, duration_minutes, action
    access_logs = [
        {"ts": "2024-05-01 09:00", "user": "Siobhan O'Sullivan", "duration": 120, "action": "File Review"},
        {"ts": "2024-05-01 11:30", "user": "John Doe", "duration": 15, "action": "Unauthorized Copy"}, 
        {"ts": "2024-05-02 10:00", "user": "Liam Murphy", "duration": 45, "action": "Drafting"},
        {"ts": "2024-05-02 14:00", "user": "Aisling Quinn", "duration": 30, "action": "Evidence Tagging"},
        {"ts": "2024-05-03 16:00", "user": "Jane Smith", "duration": 10, "action": "File Browsing"}, 
        {"ts": "2024-05-03 17:00", "user": "Siobhan O'Sullivan", "duration": 200, "action": "Brief Writing"},
        {"ts": "2024-05-04 08:30", "user": "Liam Murphy", "duration": 60, "action": "Consultation"}
    ]
    
    # 将日志转换为混淆的 .sec 格式，模拟专有加密文件，强迫调用 Decryptor Skill
    json_str = json.dumps(access_logs)
    encoded_bytes = base64.b64encode(json_str.encode('utf-8'))
    
    with open("case_files/access_logs.sec", "wb") as f:
        f.write(encoded_bytes)

    # 干扰文件
    with open("case_files/notes.tmp", "w") as f:
        f.write("Don't forget to buy more coffee beans.\nIAM Migration is such a headache.")

if __name__ == "__main__":
    build_env()
