import os
import argparse
import json
import csv

def build_turn_1():
    # 建立初始目录
    os.makedirs("pending_contractors", exist_ok=True)
    os.makedirs("building_specs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 大楼规格：ID, 面积(sqft), 预估工时, 基准单价(per sqft)
    buildings = [
        {"bid": "BLD_001", "name": "Sunset Plaza", "sqft": 50000, "est_hours": 120, "base_price": 0.50, "class": "A"},
        {"bid": "BLD_002", "name": "Industrial Hub", "sqft": 120000, "est_hours": 300, "base_price": 0.35, "class": "B"},
        {"bid": "BLD_003", "name": "Downtown Tower", "sqft": 80000, "est_hours": 200, "base_price": 0.60, "class": "A"}
    ]
    with open("building_specs/specs.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=buildings[0].keys())
        writer.writeheader()
        writer.writerows(buildings)

    # 承包商数据
    contractors = [
        {
            "id": "C_001", "name": "Sparkle Clean Co", "level": "A", "quote_type": "total", "quote_val": 28000, 
            "rating": 4.5, "tags": ["Green-Eco", "Local"], "target_bid": "BLD_001"
        }, # 溢价 28000 / (50000*0.5) = 1.12 < 1.2 (PASS)
        {
            "id": "C_002", "name": "Budget Janitors", "level": "C", "quote_type": "hourly", "quote_val": 25, 
            "rating": 3.2, "tags": [], "target_bid": "BLD_002"
        }, # Level C (FAIL), Rating low (FAIL)
        {
            "id": "C_003", "name": "Elite Services", "level": "B", "quote_type": "total", "quote_val": 45000, 
            "rating": 4.8, "tags": ["Green-Eco"], "target_bid": "BLD_003"
        } # 45000 / (80000*0.6) = 0.93 (PASS)
    ]
    for c in contractors:
        with open(f"pending_contractors/{c['id']}.json", "w") as f:
            json.dump(c, f)

    # 违规日志
    violations = [
        {"cid": "C_001", "date": "2023-01-10", "type": "Late arrival"},
        {"cid": "C_003", "date": "2023-05-12", "type": "Safety breach"},
        {"cid": "C_003", "date": "2023-06-01", "type": "Incomplete cleaning"}
    ]
    with open("logs/violation_records.json", "w") as f:
        json.dump(violations, f)

def build_turn_2():
    os.makedirs("emergency_updates", exist_ok=True)
    os.makedirs("insurance_check", exist_ok=True)
    
    # 新承包商：看似完美但报价极高
    new_c = {
        "id": "C_004", "name": "Rapid Response", "level": "A", "quote_type": "total", "quote_val": 35000, 
        "rating": 4.9, "tags": [], "target_bid": "BLD_001"
    } # 35000 / 25000 = 1.4 > 1.2 (FAIL per Turn 1 rule)
    with open(f"emergency_updates/{new_c['id']}.json", "w") as f:
        json.dump(new_c, f)

    # 保险状态
    insurance = [
        {"id": "C_001", "status": "Expired", "expiry_date": "2023-12-01"},
        {"id": "C_003", "status": "Active", "expiry_date": "2024-12-01"},
        {"id": "C_004", "status": "Active", "expiry_date": "2025-01-01"}
    ]
    with open("insurance_check/latest_status.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=insurance[0].keys())
        writer.writeheader()
        writer.writerows(insurance)

def build_turn_3():
    # 第三轮主要是规则逻辑变更，不引入大量新文件，但修改原有逻辑。
    # 模拟在 logs 目录下增加一个补充备注文件
    with open("logs/hq_memo.txt", "w") as f:
        f.write("Note: Audit team focusing on A-class building safety. Contractor rating history is critical.")

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
