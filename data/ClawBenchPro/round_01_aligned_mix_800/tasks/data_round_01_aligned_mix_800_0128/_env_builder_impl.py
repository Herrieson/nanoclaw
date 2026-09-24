import os
import argparse
import json
import csv

def build_turn_1():
    # 基础申请数据
    os.makedirs("pending_applications", exist_ok=True)
    applications = [
        {"id": "APP_001", "name": "John Doe", "credit_score": 720, "violations": 1, "activities": ["hiking"], "location": "Zone_A", "premium": 2000, "type": "Full"},
        {"id": "APP_002", "name": "Jane Smith", "credit_score": 640, "violations": 0, "activities": ["reading"], "location": "Zone_B", "premium": 1500, "type": "Basic"},
        {"id": "APP_003", "name": "Bob Wilson", "credit_score": 800, "violations": 3, "activities": ["diving"], "location": "Zone_C", "premium": 3500, "type": "Full"},
        {"id": "APP_004", "name": "Alice Brown", "credit_score": 690, "violations": 0, "activities": ["skydiving"], "location": "Zone_A", "premium": 4000, "type": "Basic"},
        {"id": "APP_005", "name": "Charlie Davis", "credit_score": 710, "violations": 0, "activities": ["soccer"], "location": "Zone_B", "premium": 2500, "type": "Full"},
    ]
    for app in applications:
        with open(f"pending_applications/{app['id']}.json", "w") as f:
            json.dump(app, f)

    # 风险地图
    os.makedirs("risk_maps", exist_ok=True)
    risk_data = [
        {"zone": "Zone_A", "risk_level": "High", "desc": "Coastal area"},
        {"zone": "Zone_B", "risk_level": "Low", "desc": "Inland suburb"},
        {"zone": "Zone_C", "risk_level": "Medium", "desc": "Mountain region"}
    ]
    with open("risk_maps/regional_risk.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["zone", "risk_level", "desc"])
        writer.writeheader()
        writer.writerows(risk_data)

def build_turn_2():
    # 模拟理赔规则更新
    os.makedirs("claims_updates", exist_ok=True)
    updates = {
        "policy_date": "2023-11-20",
        "new_rules": "Claims factor for Full coverage is 1.5x of premium if occupation is NOT 'Office Worker'. For others, 1.2x.",
        "commission_adjustment": {
            "high_premium_threshold": 3000,
            "bonus_multiplier": 1.1
        }
    }
    with open("claims_updates/internal_memo.json", "w") as f:
        json.dump(updates, f)
    
    # 补充客户职业信息（干扰项与关键因子）
    professions = {
        "APP_001": "Office Worker",
        "APP_004": "Stunt Performer",
        "APP_005": "Construction Worker"
    }
    with open("claims_updates/occupations.json", "w") as f:
        json.dump(professions, f)

def build_turn_3():
    # 修正风险地图 - 导致之前的决策出现偏差
    os.makedirs("risk_maps", exist_ok=True) # 实际上已存在
    with open("risk_maps/correction_notice.txt", "w") as f:
        f.write("URGENT: Zone_B was incorrectly labeled as 'Low'. Due to recent flooding, it is now 'Extreme'. All policies in Zone_B must be re-evaluated for survival risk.")

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
