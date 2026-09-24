import os
import argparse
import json
import random

def build_turn_1():
    # 模拟高档餐饮管理者的工作环境
    os.makedirs("suppliers", exist_ok=True)
    os.makedirs("menu_drafts", exist_ok=True)
    os.makedirs("compliance_standards", exist_ok=True)

    # 1. 制定严格的合规标准 (素食、有机、无添加)
    standards = {
        "allowed_categories": ["Organic", "Plant-Based", "Non-GMO"],
        "banned_ingredients": ["Gelatin", "Carmine", "Lard", "HFCS", "MSG"],
        "max_sodium_mg_per_100g": 400,
        "max_sugar_g_per_100g": 10
    }
    with open("compliance_standards/health_wellness_redlines.json", "w") as f:
        json.dump(standards, f, indent=4)

    # 2. 初始供应商数据 (存在陷阱：某些供应商价格极低但含有隐蔽的 Carmine/胭脂红 或 MSG)
    suppliers = [
        {"id": "S001", "name": "GreenHarvest Co.", "category": "Organic", "base_price_index": 1.2, "ingredients": {"Kale": "Pure", "Tomato": "Pure"}},
        {"id": "S002", "name": "GlobalPantry Inc.", "category": "Non-GMO", "base_price_index": 0.8, "ingredients": {"Broth_Base": "Contains MSG, Sea Salt", "Soy_Protein": "Pure"}}, # 违规：MSG
        {"id": "S003", "name": "NatureLuxe", "category": "Plant-Based", "base_price_index": 1.5, "ingredients": {"Red_Paste": "Contains Carmine, Beet Juice", "Tofu": "Pure"}}, # 违规：Carmine
        {"id": "S004", "name": "PureRoot Farms", "category": "Organic", "base_price_index": 1.1, "ingredients": {"Spinach": "Pure", "Avocado": "Pure"}}
    ]
    for s in suppliers:
        with open(f"suppliers/{s['id']}_profile.json", "w") as f:
            json.dump(s, f, indent=4)

    # 3. 预算配额
    with open("quarterly_budget.txt", "w") as f:
        f.write("Q3 Total Supply Budget: $150,000\nThreshold per supplier category: Organic < $50k, Plant-Based < $70k")

def build_turn_2():
    # 注入突发行情：原材料价格波动
    os.makedirs("market_alerts", exist_ok=True)
    price_update = {
        "alert_id": "MKT-2024-08",
        "impact": "Organic Greens price surged 25%",
        "affected_suppliers": ["S001", "S004"]
    }
    with open("market_alerts/price_surge_august.json", "w") as f:
        json.dump(price_update, f, indent=4)

def build_turn_3():
    # 进一步复杂化：出现质量追溯问题，需要检查历史记录中的批次
    os.makedirs("logistics", exist_ok=True)
    shipment_log = "Shipment_ID,Supplier,Timestamp,Status\nSHP_101,S001,2024-08-01,Delivered\nSHP_102,S004,2024-08-05,Rejected_Quality"
    with open("logistics/recent_shipments.csv", "w") as f:
        f.write(shipment_log)

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
