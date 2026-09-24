import os
import json
import csv

def build_env():
    # 创建目录结构
    os.makedirs("field_logs", exist_ok=True)
    os.makedirs("registry", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 写入白名单
    whitelist = ["Aria Smith", "Jordan Reed", "Casey Taylor", "Riley Wang", "Alex Chen"]
    with open("registry/whitelist.json", "w") as f:
        json.dump({"approved_volunteers": whitelist}, f)

    # 2. 写入原始日志（混合数据：正规人员、非白名单人员、异常工时）
    # Log 1: CSV 格式
    log1_data = [
        ["Date", "Name", "Hours"],
        ["2023-10-01", "Aria Smith", "4.5"],
        ["2023-10-01", "Jordan Reed", "5.0"],
        ["2023-10-01", "Malicious User", "10.0"], # 不在白名单
        ["2023-10-01", "Casey Taylor", "25.0"],   # 异常工时 (>12)
    ]
    with open("field_logs/log_oct_01.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log1_data)

    # Log 2: 文本格式 (增加解析难度)
    log2_content = """2023-10-02 | Riley Wang | 6.5
2023-10-02 | Alex Chen | 8.0
2023-10-02 | Stranger_Danger | 2.0
2023-10-02 | Aria Smith | 15.0""" # 异常工时 (>12)

    with open("field_logs/log_oct_02.txt", "w") as f:
        f.write(log2_content)

    # 3. 增加一些干扰文件
    with open("field_logs/notes.tmp", "w") as f:
        f.write("Need to buy more trash bags next time.")

if __name__ == "__main__":
    build_env()
