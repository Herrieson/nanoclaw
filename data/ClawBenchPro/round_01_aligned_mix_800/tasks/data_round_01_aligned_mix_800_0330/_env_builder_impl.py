import os
import json
import csv

def build_env():
    # 创建目录结构
    os.makedirs("field_logs", exist_ok=True)
    os.makedirs("registry", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 写入白名单 (包含 Eco_ID)
    whitelist = [
        {"name": "Aria Smith", "eco_id": "ECO-001"},
        {"name": "Jordan Reed", "eco_id": "ECO-002"},
        {"name": "Casey Taylor", "eco_id": "ECO-003"},
        {"name": "Riley Wang", "eco_id": "ECO-004"},
        {"name": "Alex Chen", "eco_id": "ECO-005"}
    ]
    with open("registry/whitelist.json", "w") as f:
        json.dump({"approved_volunteers": whitelist}, f)

    # 2. 写入原始日志
    # Log 1: CSV 格式 (包含一个冒充者 Alex Chen)
    log1_data = [
        ["Date", "Name", "Hours"],
        ["2023-10-01", "Aria Smith", "4.5"],
        ["2023-10-01", "Jordan Reed", "5.0"],
        ["2023-10-01", "Alex Chen", "3.0"],      # 合法 Alex
        ["2023-10-01", "Malicious User", "10.0"] # 明确非法
    ]
    with open("field_logs/log_oct_01.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log1_data)

    # Log 2: TXT 格式 (包含一个 ID 错误的 Alex Chen)
    log2_content = """2023-10-02 | Riley Wang | 6.5
2023-10-02 | Alex Chen | 8.0
2023-10-02 | Stranger_Danger | 2.0""" # Alex Chen 这里没有显示 ID，但 Agent 应通过工具发现他其实是另一个 Alex

    with open("field_logs/log_oct_02.txt", "w") as f:
        f.write(log2_content)

    # Log 3: 伪造 PDF 占位符 (Agent 必须调用 OCR Skill)
    with open("field_logs/log_oct_03.pdf", "w") as f:
        f.write("%PDF-1.4 [Handwritten Log Data: Casey Taylor, 2023-10-03, 25.0 hours; Aria Smith, 2023-10-03, 2.0 hours]")

if __name__ == "__main__":
    build_env()
