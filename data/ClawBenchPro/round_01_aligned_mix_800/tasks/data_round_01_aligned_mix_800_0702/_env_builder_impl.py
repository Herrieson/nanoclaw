import os
import csv
import random

def build_env():
    # 创建目录
    os.makedirs("warehouse_reports", exist_ok=True)
    os.makedirs("accounting", exist_ok=True)

    # 金属市价 (USD/kg)
    prices = {
        "Copper": 8.5,
        "Zinc": 2.4,
        "Nickel": 16.2,
        "Aluminum": 2.1
    }

    # 生成 CSV 原始数据 (带噪音和重复)
    csv_file = "warehouse_reports/inventory_log_a.csv"
    data = [
        ["batch_id", "mineral", "weight_kg", "purity_pct"],
        ["B001", "Copper", "1200", "88.5%"],
        ["B002", "Nickel", "500", "82.0"],  # 不合格
        ["B003", "Zinc", "2000kg", "91"],
        ["B001", "Copper", "1200", "88.5%"], # 重复
        ["B004", "Aluminum", "3500", "78.2%"], # 不合格
        ["B005", "Nickel", "800", "86.5"],
    ]
    
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    # 生成 文本日志 数据
    log_file = "warehouse_reports/manual_notes.txt"
    notes = [
        "BATCH: B006 | MATERIAL: Copper | QTY: 450 | QUALITY: 89.2%",
        "BATCH: B007 | MATERIAL: Zinc | QTY: 1100kg | QUALITY: 84.5", # 不合格
        "BATCH: B008 | MATERIAL: Nickel | QTY: 300 | QUALITY: 92.1%"
    ]
    
    with open(log_file, "w") as f:
        f.write("\n".join(notes))

if __name__ == "__main__":
    build_env()
