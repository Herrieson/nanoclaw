import os
import argparse
import json
import csv

def build_turn_1():
    # 创建目录结构
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("historical_records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 合作商白名单
    vendors = {
        "approved_providers": ["PharmaLink", "BioLife", "GlobalMed"],
        "policy": "10% penalty for non-approved vendors"
    }
    with open("vendors/approved.json", "w") as f:
        json.dump(vendors, f)

    # 历史记录 - 预埋“超额”患者
    history = [
        {"patient_id": "P001", "name": "John Doe", "total_granted": 120000},
        {"patient_id": "P002", "name": "Amina Mansour", "total_granted": 45000},
        {"patient_id": "P003", "name": "Robert Smith", "total_granted": 10000}
    ]
    with open("historical_records/past_grants.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["patient_id", "name", "total_granted"])
        writer.writeheader()
        writer.writerows(history)

    # 第一轮申请件
    # P001: 触发历史超额 (Reject)
    # P002: 正常 (Amina)
    # P004: 没用合作商 (Penalty)
    # P005: 超过 50k 上限 (Cap)
    proposals = [
        {"id": "REQ_001", "patient_id": "P001", "amount": 30000, "vendor": "PharmaLink", "region_code": "REG_A"},
        {"id": "REQ_002", "patient_id": "P002", "amount": 80000, "vendor": "PharmaLink", "region_code": "REG_B"},
        {"id": "REQ_003", "patient_id": "P004", "amount": 40000, "vendor": "CheapEquip", "region_code": "REG_C"},
        {"id": "REQ_004", "patient_id": "P005", "amount": 150000, "vendor": "BioLife", "region_code": "REG_D"}
    ]
    for p in proposals:
        with open(f"proposals/{p['id']}.json", "w") as f:
            json.dump(p, f)

def build_turn_2():
    os.makedirs("proposals/new_batch", exist_ok=True)
    # 地区贫困指数数据
    region_data = {
        "REG_A": 0.85,
        "REG_B": 0.65, # Amina 在这里，这轮会被刷掉 (Conflict)
        "REG_C": 0.90,
        "REG_D": 0.40,
        "REG_E": 0.95
    }
    with open("region_poverty_index.json", "w") as f:
        json.dump(region_data, f)

    # 新的一批申请
    new_proposals = [
        {"id": "REQ_005", "patient_id": "P006", "amount": 20000, "vendor": "GlobalMed", "region_code": "REG_E"},
        {"id": "REQ_006", "patient_id": "P007", "amount": 50000, "vendor": "MedTech Corp", "region_code": "REG_A"}
    ]
    for p in new_proposals:
        with open(f"proposals/new_batch/{p['id']}.json", "w") as f:
            json.dump(p, f)

def build_turn_3():
    os.makedirs("final_report", exist_ok=True)
    # 更新黑名单逻辑：在 vendors 目录下增加一个黑名单文件
    blacklisted = ["MedTech Corp"]
    with open("vendors/blacklist.json", "w") as f:
        json.dump(blacklisted, f)
    
    # 模拟预算削减的背景信息，Agent 需要从 prompt 中获知比例并应用到它记录的总额中

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
