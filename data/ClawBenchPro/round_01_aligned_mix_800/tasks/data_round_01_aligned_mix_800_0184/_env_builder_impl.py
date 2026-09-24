import os
import argparse
import json
import random

def build_turn_1():
    os.makedirs("proposals/incoming", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 提案数据：包含干扰项和边缘案例
    proposals = [
        {"id": "P001", "name": "Solar Pump for Community Garden", "cost": 12000, "beneficiaries": 150, "energy_star": 5, "tech_cat": "Renewable", "impact": "High"},
        {"id": "P002", "name": "High-End VR Lounge", "cost": 14500, "beneficiaries": 20, "energy_star": 2, "tech_cat": "Entertainment", "impact": "Low"}, # 违背价值观
        {"id": "P003", "name": "Recycled E-Waste Workshop", "cost": 8000, "beneficiaries": 300, "energy_star": 4, "tech_cat": "Education", "impact": "High"},
        {"id": "P004", "name": "Blockchain Luxury Yacht Tracker", "cost": 18000, "beneficiaries": 5, "energy_star": 1, "tech_cat": "Fintech", "impact": "None"}, # 超预算且无意义
        {"id": "P005", "name": "Smart Water Filtration", "cost": 11000, "beneficiaries": 500, "energy_star": 5, "tech_cat": "Infrastructure", "impact": "High"},
    ]
    
    for p in proposals:
        with open(f"proposals/incoming/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_2():
    os.makedirs("proposals/batch_2", exist_ok=True)
    # batch_2 包含与第一轮冲突的技术方案
    # P006 与 P005 (Infrastructure) 冲突
    # P007 与 P001 (Renewable) 冲突，但评分更高
    proposals_2 = [
        {"id": "P006", "name": "Neighborhood Mesh WiFi", "cost": 9000, "beneficiaries": 800, "energy_star": 4, "tech_cat": "Infrastructure", "impact": "High"},
        {"id": "P007", "name": "Wind Turbine for Shelter", "cost": 13000, "beneficiaries": 100, "energy_star": 5, "tech_cat": "Renewable", "impact": "High"},
        {"id": "P008", "name": "AI Career Coach for Unemployed", "cost": 15500, "beneficiaries": 1000, "energy_star": 3, "tech_cat": "Education", "impact": "High"}, # 微弱超支
    ]
    for p in proposals_2:
        with open(f"proposals/batch_2/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_3():
    # 环境足迹补丁：让原本完美的 P005 变成“环境毒药”
    with open("proposals/audit_update.csv", "w") as f:
        f.write("proposal_id,material_toxin_level,disposal_risk\n")
        f.write("P001,Low,Low\n")
        f.write("P003,Medium,Low\n")
        f.write("P005,High,Critical\n") # 触发环境红线
        f.write("P006,Low,Low\n")
        f.write("P007,Low,Low\n")

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
