import os
import pandas as pd
import json

def build_env():
    # 创建目录
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0290", exist_ok=True)

    # 1. 员工数据
    staff_data = [
        {"id": "S001", "name": "Elena Akana", "role": "Non-Retail Sales"},
        {"id": "S002", "name": "Kai Mana", "role": "Non-Retail Sales"},
        {"id": "S003", "name": "Luka Chen", "role": "Retail Counter"}, # 干扰项
        {"id": "S004", "name": "Mele Hina", "role": "Non-Retail Sales"},
        {"id": "S005", "name": "Admin Sarah", "role": "Administration"} # 干扰项
    ]
    with open("inventory/staff_registry.json", "w") as f:
        json.dump(staff_data, f)

    # 2. 资产目录 (故意移除 category 字段，迫使调用 Skill)
    asset_catalog = pd.DataFrame({
        "asset_id": ["A-01", "A-02", "A-03", "A-04"],
        "name": ["Solar Panel Kit", "Industrial Hydraulic Press", "Wind Turbine Blade", "Heavy Plastic Molding Machine"]
    })
    asset_catalog.to_csv("inventory/asset_catalog.csv", index=False)

    # 3. 成交日志
    # Elena: A-01 (10000) -> 5% = 500; A-02 (20000) -> 2.5% = 500. Total: 1000
    # Kai: A-03 (15000) -> 5% = 750; A-99 (Missing) -> Anomaly
    # Mele: A-04 (10000) -> 2.5% = 250
    # Luka (Retail): Should be ignored
    deals = [
        {"deal_id": "D101", "staff_id": "S001", "asset_id": "A-01", "amount": 10000},
        {"deal_id": "D102", "staff_id": "S001", "asset_id": "A-02", "amount": 20000},
        {"deal_id": "D103", "staff_id": "S002", "asset_id": "A-03", "amount": 15000},
        {"deal_id": "D104", "staff_id": "S002", "asset_id": "A-99", "amount": 5000}, # 异常项
        {"deal_id": "D105", "staff_id": "S003", "asset_id": "A-01", "amount": 5000},  # 零售人员
        {"deal_id": "D106", "staff_id": "S004", "asset_id": "A-04", "amount": 10000}
    ]
    pd.DataFrame(deals).to_csv("inventory/deals_log.csv", index=False)

if __name__ == "__main__":
    build_env()
