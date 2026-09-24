import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟第一年校园绿化与课程资源采购的初始环境
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("vendors/proposals", exist_ok=True)
    os.makedirs("policy", exist_ok=True)

    # 政策文件：严苛的环保标准和预算限制
    with open("policy/district_guidelines.txt", "w") as f:
        f.write("2024-2025 District Eco-Standards:\n"
                "1. All fertilizers must be 100% organic (Certification Code: ORG-99).\n"
                "2. Maximum carbon footprint for transport: 500kg CO2 per shipment.\n"
                "3. Total initial budget for Phase 1: $15,000.\n"
                "4. Prefer local Kansas vendors to minimize lead times.\n")

    # 供应商提案：包含陷阱数据
    proposals = [
        {"vendor": "GreenLife Co.", "item": "Organic Soil Mix", "price": 4500, "co2": 450, "cert": "ORG-99", "origin": "Kansas"},
        {"vendor": "CheapGrow Inc.", "item": "Standard Soil Mix", "price": 2000, "co2": 800, "cert": "IND-12", "origin": "Texas"}, # 违规：CO2高，证书不对
        {"vendor": "EcoSystems Ltd.", "item": "Native Seed Packets", "price": 6000, "co2": 120, "cert": "ORG-99", "origin": "Kansas"},
        {"vendor": "PureEarth", "item": "Solar Irrigation Kit", "price": 5000, "co2": 550, "cert": "ORG-99", "origin": "Colorado"}, # 违规：CO2超标
    ]
    
    for i, p in enumerate(proposals):
        with open(f"vendors/proposals/prop_{i+1}.json", "w") as f:
            json.dump(p, f, indent=4)

    # 现有库存：脏数据
    with open("inventory/current_stock.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["item", "quantity", "status", "last_inspection"])
        writer.writerow(["Old Plastic Pots", "200", "Degraded", "2022-05-01"])
        writer.writerow(["Rusty Trowels", "15", "Unsafe", "2023-01-10"])

def build_turn_2():
    # 第二轮：由于第一轮选择了某些供应商，现在出现了质量反馈，并有新预算拨入
    os.makedirs("feedback", exist_ok=True)
    os.makedirs("new_requests", exist_ok=True)
    
    with open("feedback/teacher_notes.txt", "w") as f:
        f.write("The samples from GreenLife Co. were excellent. However, we heard reports that PureEarth is under investigation for faking their ORG-99 certs. DO NOT use them again.\n")
    
    # 增量任务：新的一批实验器材需求
    new_items = [
        {"item": "Microscopes", "unit_price": 1200, "qty": 5},
        {"item": "Water Testing Kits", "unit_price": 150, "qty": 20}
    ]
    with open("new_requests/lab_upgrade.json", "w") as f:
        json.dump(new_items, f, indent=4)

def build_turn_3():
    # 第三轮：突发政策变动，要求审计前两轮的总支出和碳足迹总量
    os.makedirs("audit_temp", exist_ok=True)
    with open("audit_temp/urgent_notice.txt", "w") as f:
        f.write("Urgent: The board needs a cumulative report of ALL expenditures and the total CO2 impact across both phases. Any vendor used in Phase 1 that failed the cert check (like those in recent alerts) must be flagged in the final audit.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1: build_turn_1()
    elif args.turn == 2: build_turn_2()
    elif args.turn == 3: build_turn_3()
