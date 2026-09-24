import os
import csv

def build_env():
    # 创建目录结构
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 创建文学代码对照表 (Literary Codes)
    literary_codes = [
        ["code", "work_title", "material_type"],
        ["DQ01", "Don Quixote", "Oak"],
        ["UL02", "Ulysses", "Maple"],
        ["MH03", "Moby Dick", "Cedar"],
        ["OP04", "One Hundred Years of Solitude", "Mahogany"],
        ["HD05", "Heart of Darkness", "Ebony"]
    ]
    with open("reference/literary_codes.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(literary_codes)

    # 2. 创建原始日志 (包含脏数据和文学编码)
    # 格式: ID | Material | Category | Qty | UnitPrice | Status
    raw_logs = [
        "ID_001 | Oak | Wood | 10 | 150.0 | Received",      # 有效 (DQ01)
        "ID_002 | Cement | Basic | 50 | 20.0 | Received",    # 类别不对
        "ID_003 | Maple | Wood | 5 | 300.0 | Pending",      # 状态不对
        "ID_004 | Maple | Wood | 8 | 320.0 | Received",     # 有效 (UL02)
        "ID_005 | Pine | Wood | 20 | 45.0 | Received",      # 不在代码表 (Invalid)
        "ID_006 | Ebony | Wood | 2 | 6000.0 | Received",    # 有效 (HD05) 但超价
        "ID_007 | Mahogany | Wood | 12 | 450.0 | Received",  # 有效 (OP04)
        "ERROR_LOG_### | N/A | Corrupted | 0 | 0 | Error",  # 纯杂质
        "ID_008 | Cedar | Wood | 15 | 120.0 | Received"     # 有效 (MH03)
    ]
    with open("inventory/raw_logs.txt", "w", encoding="utf-8") as f:
        for line in raw_logs:
            f.write(line + "\n")

if __name__ == "__main__":
    build_env()
