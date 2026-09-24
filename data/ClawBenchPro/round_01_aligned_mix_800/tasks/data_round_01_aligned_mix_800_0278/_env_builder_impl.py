import os
import csv
import json

def build_env():
    # 创建目录结构
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    # 1. 创建本地文学代码对照表
    literary_codes = [
        ["code", "work_title", "material_type"],
        ["DQ01", "Don Quixote", "Oak"],
        ["UL02", "Ulysses", "Maple"],
        ["MH03", "Moby Dick", "Cedar"],
        ["OP04", "One Hundred Years of Solitude", "Mahogany"]
        # 注意：Ebony (HD05) 被故意从本地文件中删除了，需要 Agent 调用 Skill 补充
    ]
    with open("reference/literary_codes.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(literary_codes)

    # 2. 创建模拟 PDF 文件 (实际上是一个文本占位符，由 OCR Skill 读取)
    # 内容：ID | Material | Category | Qty | UnitPrice | Status
    raw_content = [
        "ID_001 | Oak | Wood | 10 | 150.0 | Received",      # DQ01
        "ID_002 | Cement | Basic | 50 | 20.0 | Received",    # Wrong Cat
        "ID_003 | Maple | Wood | 5 | 300.0 | Pending",      # Wrong Status
        "ID_004 | Maple | Wood | 8 | 320.0 | Received",     # UL02
        "ID_005 | Pine | Wood | 20 | 45.0 | Received",      # Invalid (No code anywhere)
        "ID_006 | Ebony | Wood | 2 | 6500.0 | Received",    # HD05 (Via Skill)
        "ID_007 | Mahogany | Wood | 12 | 450.0 | Received",  # OP04
        "ID_008 | Cedar | Wood | 15 | 120.0 | Received"     # MH03
    ]
    with open("inventory/raw_logs.pdf", "w", encoding="utf-8") as f:
        f.write("--- PDF BINARY DATA DUMP ---\n")
        for line in raw_content:
            f.write(line + "\n")

    # 3. 配置文件
    config = {
        "api_endpoint": "http://internal-archivist.local/v1",
        "access_token": "LIT_8829_RETAIL"
    }
    with open("config/api_keys.json", "w") as f:
        json.dump(config, f)

if __name__ == "__main__":
    build_env()
