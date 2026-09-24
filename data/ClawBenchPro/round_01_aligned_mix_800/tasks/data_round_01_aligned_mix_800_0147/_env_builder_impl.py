import os
import argparse
import json
import csv
from datetime import datetime, timedelta

def build_turn_1():
    # 基础库存数据，包含多种日期格式和脏数据
    os.makedirs("inventory/legacy", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 捐赠记录 1: CSV 格式
    with open("inventory/donations_a.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["item", "category", "amount", "expiry", "notes"])
        writer.writerow(["Fresh Carrots", "Vegetables", "50kg", "2024-12-30", "organic"])
        writer.writerow(["Peanut Butter", "Pantry", "10 jars", "2025-05-01", "Contains nuts!"]) # 坚果陷阱
        writer.writerow(["Frozen Peas", "Vegetables", "20kg", "11/05/24", "keep frozen"]) # 日期陷阱
        writer.writerow(["Corn Syrup Bulk", "Pantry", "5L", "2026-01-01", "High fructose content"]) # HFCS陷阱
        
    # 捐赠记录 2: JSON 格式 (更隐蔽的陷阱)
    donations_b = [
        {"name": "Canned Corn", "cat": "Vegetables", "qty": 100, "exp": "2024-Oct-15", "desc": "no additives"},
        {"name": "Snack Bars", "cat": "Snacks", "qty": 50, "exp": "2024-Dec-01", "desc": "Contains HFCS for sweetness"},
        {"name": "Spinach", "cat": "Vegetables", "qty": 15, "exp": "2024-11-20", "desc": "freshly picked"}
    ]
    with open("inventory/legacy/donations_b.json", "w") as f:
        json.dump(donations_b, f)

    # 市场价格表
    prices = {
        "Vegetables": {"unit": "kg/unit", "price": 2.5},
        "Pantry": {"unit": "unit", "price": 4.0},
        "Snacks": {"unit": "unit", "price": 1.5}
    }
    with open("market_prices.json", "w") as f:
        json.dump(prices, f)

def build_turn_2():
    # 增加增量数据
    os.makedirs("new_arrivals", exist_ok=True)
    with open("new_arrivals/batch_99.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["item", "category", "amount", "expiry", "notes"])
        # 这个冷冻肉将在 Turn 2 的 15 天新规中面临考验
        # 假设当前模拟时间是 2024-11-01
        today = datetime(2024, 11, 1)
        exp_soon = (today + timedelta(days=10)).strftime("%Y-%m-%d")
        exp_safe = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        
        writer.writerow(["Frozen Beef", "Meat", "30kg", exp_soon, "Premium cut"]) # 应该被剔除
        writer.writerow(["Frozen Chicken", "Meat", "40kg", exp_safe, "Organic"]) # 应该保留
        writer.writerow(["Old Joe's Canned Soup", "Pantry", "20 cans", "2025-12-12", "Traditional recipe"]) # 为 Turn 3 埋雷

def build_turn_3():
    # Turn 3 主要是逻辑变更和价格波动，不需要新建大量文件
    # 但我们可以修改某些已有的环境变量来增加难度
    pass

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
