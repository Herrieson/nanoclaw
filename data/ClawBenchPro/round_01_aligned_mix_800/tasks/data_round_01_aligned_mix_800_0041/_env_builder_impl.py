import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("raw_assets", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    # 财务规则：残值 = 原价 * (1 - 折旧率 * 使用年数)
    with open("docs/finance_rules.txt", "w") as f:
        f.write("Financial Protocol v1.0\n")
        f.write("Depreciation Rule: Residual_Value = Original_Price * (1 - Annual_Rate * Years_Used)\n")
        f.write("Base Annual Rate: Electronics 0.15, Furniture 0.05, Art_Supplies 0.20\n")
        f.write("Scrap Threshold: Residual_Value < 15.0\n")

    # 资产数据 - 包含脏数据和潜在陷阱
    assets = [
        {"id": "E001", "name": "Wacom Tablet", "type": "Electronics", "price": 200, "years": 2}, # 残值 140
        {"id": "E002", "name": "Broken iPad", "type": "Electronics", "price": 500, "years": 6}, # 残值 50 (残值低)
        {"id": "F001", "name": "Easel", "type": "Furniture", "price": 40, "years": 10}, # 残值 20
        {"id": "A001", "name": "Oil Paint Set", "type": "Art_Supplies", "price": 80, "years": 4}, # 残值 16
        {"id": "A002", "name": "Sketchbook Batch", "type": "Art_Supplies", "price": 20, "years": 1}, # 残值 16
        {"id": "X999", "name": "Ghost Item", "type": "Unknown", "price": "ERROR", "years": 0} # 脏数据
    ]
    
    with open("raw_assets/inventory_a.json", "w") as f:
        json.dump(assets[:3], f)
    
    with open("raw_assets/inventory_b.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "type", "price", "years"])
        for item in assets[3:]:
            writer.writerow([item["id"], item["name"], item["type"], item["price"], item["years"]])

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 政策变更：电子设备折旧率翻倍，报废阈值提高
    policy = {
        "policy_id": "BD-2024-05",
        "changes": {
            "Electronics_Rate": 0.30,
            "New_Scrap_Threshold": 25.0,
            "Emergency_Tax": 0.05 # 额外从残值中扣除
        }
    }
    with open("updates/new_policy.pdf.json", "w") as f:
        json.dump(policy, f)
    
    # 新货清单 - 存在陷阱：看似昂贵但折旧极快
    with open("updates/new_shipment.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "type", "price", "years"])
        writer.writerow(["E003", "Old Server", "Electronics", "100", "2"]) # 在新规下必报废

def build_turn_3():
    os.makedirs("merger_chaos", exist_ok=True)
    
    # 合并冲突数据
    # E001 在另一边也有，但价格和年限不同，甚至状态描述矛盾
    conflict_data = [
        {"id": "E001", "name": "Wacom Tablet Pro", "type": "Electronics", "price": 250, "years": 1, "status": "Fair"},
        {"id": "F005", "name": "Sculpture Stand", "type": "Furniture", "price": 120, "years": 2, "status": "Broken"}
    ]
    with open("merger_chaos/legacy_club_list.json", "w") as f:
        json.dump(conflict_data, f)
        
    # 时间戳文件，用于判断冲突
    with open("merger_chaos/metadata.txt", "w") as f:
        f.write("Inventory_A: Verified 2023-10-01\n")
        f.write("Legacy_Club_List: Verified 2024-01-15\n") # 较新，应以此为准但需逻辑判断

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
