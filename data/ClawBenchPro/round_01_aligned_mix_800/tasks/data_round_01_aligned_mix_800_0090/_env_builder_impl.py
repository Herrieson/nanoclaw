import os
import argparse
import json
import random

def build_turn_1():
    os.makedirs("contracts/pending_review", exist_ok=True)
    
    # 合同1: 表面高收益，但环保分极低 (毒药项)
    contract_a = {
        "id": "CON-2024-001",
        "client": "DeepEarth Mining Co.",
        "eco_score": 45,
        "equipment": "Heavy Metal Excavator",
        "terms": "Base $5000/mo + $200 per operating hour. Min 100 hours guaranteed.",
        "location": "Nevada Desert"
    }
    
    # 合同2: 刚好踩线，属于复杂判定 (边缘项)
    contract_b = {
        "id": "CON-2024-002",
        "client": "GreenEnergy Logistics",
        "eco_score": 68,
        "equipment": "Heavy Metal Excavator", # 环保分68且是重金属挖掘，应被拒绝
        "terms": "Flat rate $12000/mo.",
        "location": "Sacramento Delta"
    }

    # 合同3: 优质合规项
    contract_c = {
        "id": "CON-2024-003",
        "client": "SolarWind Maintenance",
        "eco_score": 85,
        "equipment": "Standard Crane",
        "terms": "Step discount: $8000 for first 3 months, then $7000.",
        "location": "Mojave Forest"
    }
    
    # 合同4: 隐藏陷阱 (Turn 2 才会暴雷)
    contract_d = {
        "id": "CON-2024-004",
        "client": "Coastal Infrastructure Ltd.",
        "eco_score": 76,
        "equipment": "Deep-sea Dredger",
        "terms": "$15000/mo. Maintenance included.",
        "location": "San Francisco Bay Marshlands"
    }

    for c in [contract_a, contract_b, contract_c, contract_d]:
        with open(f"contracts/pending_review/{c['id']}.json", "w") as f:
            json.dump(c, f, indent=4)
            
    # 模拟附件中的折旧率
    os.makedirs("contracts/appendices", exist_ok=True)
    with open("contracts/appendices/appendix_c.txt", "w") as f:
        f.write("Depreciation Rates:\n- Heavy Machinery: 12% p.a.\n- Transport Vehicles: 15% p.a.\n- Specialized Ocean Gear: 20% p.a.")

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    os.makedirs("contracts/new_batch", exist_ok=True)
    
    # 政策变更：禁止所有涉及“Marshlands（湿地）”的项目，无论分值。
    # 这会导致 Turn 1 的 contract_d 变为不合规。
    with open("updates/policy_change.pdf.txt", "w") as f:
        f.write("MEMORANDUM\nTo: Leasing Department\nSubject: Environmental Compliance Update\nEffective immediately, all projects located in 'Marshlands' or 'Protected Estuaries' are classified as High Risk (Red Line), regardless of the client's eco_score. Furthermore, any client associated with 'DeepEarth Group' is to be blacklisted due to recent spills.")

    # 新批次申请
    contract_e = {
        "id": "CON-2024-005",
        "client": "SkyHigh Wind Farms",
        "eco_score": 92,
        "equipment": "Blade Transport Trailer",
        "terms": "Fixed $9000/mo.",
        "location": "Wyoming Plains"
    }
    with open("contracts/new_batch/CON-2024-005.json", "w") as f:
        json.dump(contract_e, f, indent=4)

def build_turn_3():
    # 第三轮主要是逻辑触发，不需要大量新文件，但注入一个母公司关联表
    os.makedirs("corporate_data", exist_ok=True)
    # Coastal Infrastructure Ltd. (from Turn 1) is actually owned by DeepEarth Group (Blacklisted in Turn 2)
    mapping = {
        "DeepEarth Group": ["DeepEarth Mining Co.", "Coastal Infrastructure Ltd."],
        "EcoHoldings": ["SolarWind Maintenance", "GreenEnergy Logistics"]
    }
    with open("corporate_data/subsidiaries.json", "w") as f:
        json.dump(mapping, f, indent=4)

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
