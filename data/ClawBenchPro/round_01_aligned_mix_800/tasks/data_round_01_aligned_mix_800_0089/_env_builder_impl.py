import os
import argparse
import json
import csv

def build_turn_1():
    # 创建初始目录
    os.makedirs("raw_data/suppliers", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商数据 A：看起来最便宜但缺乏认证（陷阱：没有可持续标签）
    supplier_a = [
        {"item": "Chicken Breast", "price_per_kg": 5.5, "tags": "Bulk, Frozen", "stock": 500},
        {"item": "Beef Chuck", "price_per_kg": 8.0, "tags": "Standard", "stock": 300},
        {"item": "Rice", "price_per_kg": 1.2, "tags": "Industrial", "stock": 1000}
    ]
    
    # 供应商 B：昂贵的有机店（极其昂贵，会导致预算超标）
    supplier_b = [
        {"item": "Organic Chicken", "price_per_kg": 18.0, "tags": "Sustainable, Fair Trade, Organic", "stock": 100},
        {"item": "Quinoa", "price_per_kg": 6.5, "tags": "Fair Trade, Organic", "stock": 200}
    ]

    # 供应商 C：性价比平衡点（符合 Maria 要求的可持续标签，但蛋白质价格略高于 A，低于 B）
    # 逻辑点：Agent 必须发现 C 的 Chicken 符合 "Sustainable" 且价格能接受
    supplier_c = [
        {"item": "Pasture-Raised Chicken", "price_per_kg": 9.5, "tags": "Sustainable", "stock": 150},
        {"item": "Grass-fed Beef", "price_per_kg": 14.0, "tags": "Sustainable, Fair Trade", "stock": 80},
        {"item": "Brown Rice", "price_per_kg": 2.5, "tags": "Fair Trade", "stock": 500},
        {"item": "Seasonal Vegetables", "price_per_kg": 3.0, "tags": "Local, Sustainable", "stock": 400}
    ]

    # 供应商 D：专门的蔬菜商
    supplier_d = [
        {"item": "Mixed Greens", "price_per_kg": 2.8, "tags": "Sustainable", "stock": 300},
        {"item": "Potatoes", "price_per_kg": 1.5, "tags": "Sustainable", "stock": 600}
    ]

    for name, data in zip(["global_foods.csv", "premium_organic.csv", "green_valley.json", "roots_farm.json"], 
                          [supplier_a, supplier_b, supplier_c, supplier_d]):
        path = os.path.join("raw_data/suppliers", name)
        if name.endswith(".csv"):
            with open(path, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        else:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)

def build_turn_2():
    # 模拟 Turn 2 的动态增量
    os.makedirs("raw_data/market_updates", exist_ok=True)
    
    # 市场波动：蔬菜价格大幅上涨
    market_news = {
        "date": "2024-05-20",
        "inflation_index": "+15%",
        "price_changes": [
            {"item": "Mixed Greens", "new_price_per_kg": 4.5},
            {"item": "Potatoes", "new_price_per_kg": 2.8},
            {"item": "Brown Rice", "new_price_per_kg": 3.2}
        ],
        "blacklist_alert": "Green Valley (supplier_c) has been flagged for unethical labor practices in their poultry division."
    }
    
    # 逻辑陷阱：由于 Green Valley (C) 被拉黑，Agent 必须转向昂贵的 B 或寻找其他组合，
    # 且因为蔬菜涨价，原本宽裕的 $2500 预算会变得极其紧张，需要精确计算蛋白质和蔬菜的最低限度。
    
    with open("raw_data/market_updates/alert_log.json", "w") as f:
        json.dump(market_news, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
