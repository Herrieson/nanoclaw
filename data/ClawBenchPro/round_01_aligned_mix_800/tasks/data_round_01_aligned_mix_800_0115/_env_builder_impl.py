import os
import argparse
import json
import csv

def build_turn_1():
    # 路径已在 assets/data_round_01_aligned_mix_800_0115/turn_1
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("policies", exist_ok=True)
    
    # 初始合规政策：含复杂的阈值计算
    policy = {
        "lab_id": "PHYS-CHM-1330",
        "hazmat_limits": {
            "Flammable": 50.0, # L
            "Toxic": 10.0,     # kg
            "Corrosive": 25.0  # L
        },
        "instability_index_threshold": 0.85,
        "note": "Any substance with index > threshold counts double towards total category limit."
    }
    with open("policies/safety_protocol_v1.json", "w") as f:
        json.dump(policy, f, indent=4)

    # 现有库存：包含脏数据和矛盾点
    inventory = [
        ["id", "name", "cas", "category", "amount", "unit", "instability_index", "status"],
        ["S001", "Ethanol", "64-17-5", "Flammable", "20.0", "L", "0.2", "In-Stock"],
        ["S002", "Benzene", "71-43-2", "Flammable", "15.0", "L", "0.9", "In-Stock"], # Index 0.9 > 0.85, counts as 30.0
        ["S003", "Hydrochloric Acid", "7647-01-0", "Corrosive", "10.0", "L", "0.5", "In-Stock"],
        ["S004", "Sodium Cyanide", "143-33-9", "Toxic", "4.0", "kg", "0.95", "In-Stock"], # Index 0.95 > 0.85, counts as 8.0
        ["S005", "Unknown Crystal", "NULL", "Toxic", "3.0", "kg", "0.4", "Pending-Arrival"]
    ]
    with open("inventory/current_stock.csv", "w", newline='') as f:
        csv.writer(f).writerows(inventory)

    # 申领记录：需要交叉对比
    requests = [
        {"req_id": "REQ-882", "substance": "Benzene", "approved": True, "delivered": False},
        {"req_id": "REQ-883", "substance": "Sulfuric Acid", "approved": True, "delivered": False, "amount": 5.0, "unit": "L", "cat": "Corrosive", "index": 0.3}
    ]
    with open("inventory/pending_requests.json", "w") as f:
        json.dump(requests, f, indent=4)

def build_turn_2():
    # 模拟环境演进：turn_2 已包含 turn_1 的产物
    # 增加突发政策文件，但不删除旧文件，增加干扰
    os.makedirs("emergency_updates", exist_ok=True)
    new_rules = """
    # EMERGENCY NOTICE: VENTILATION FAILURE
    Date: 2023-10-27
    Subject: Immediate VOC Reduction
    
    All Volatile Organic Compounds (VOC) category limits (primarily Flammable items) 
    are reduced by 40% effective immediately. 
    Current limits are now 60% of the values stated in safety_protocol_v1.json.
    """
    with open("emergency_updates/notice_oct_27.txt", "w") as f:
        f.write(new_rules)

def build_turn_3():
    # 增加捐赠清单
    os.makedirs("donations", exist_ok=True)
    donations = [
        ["item_name", "category", "amount", "unit", "instability_index", "historical_value"],
        ["Vintage Mercury Thermometer Set", "Toxic", "2.5", "kg", "0.1", "High"], # 合规但增加重量
        ["19th Century Picric Acid Bottle", "Flammable", "2.0", "L", "0.99", "Extreme"], # 高风险，翻倍计算
        ["Pure Chloroform Sample", "Toxic", "1.0", "kg", "0.3", "Medium"]
    ]
    with open("donations/scientific_artifacts.csv", "w", newline='') as f:
        csv.writer(f).writerows(donations)

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
