import os
import argparse
import json
import csv

def build_turn_1():
    # 建立目录结构
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("requests", exist_ok=True)
    os.makedirs("town_rules", exist_ok=True)

    # 库存数据：故意设置一些库存极少的诱导项
    inventory = [
        ["item", "stock", "cost_price", "suggested_price"],
        ["Quest 3 VR", "2", "450", "550"],
        ["Steam Deck", "5", "350", "420"],
        ["AirPods Pro 3", "10", "180", "240"],
        ["Raspberry Pi 5", "3", "60", "95"],
        ["Mechanical Keyboard", "4", "80", "130"]
    ]
    with open("inventory/current_stock.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

    # 客户请求：复杂的地点和需求
    requests = {
        "orders": [
            {"customer": "Alice", "town": "Superior", "item": "Quest 3 VR", "quantity": 1},
            {"customer": "Bob", "town": "Ashland", "item": "Steam Deck", "quantity": 3},
            {"customer": "Charlie", "town": "Superior", "item": "Steam Deck", "quantity": 3}, # 导致库存冲突
            {"customer": "David", "town": "Rice Lake", "item": "Mechanical Keyboard", "quantity": 5}, # 超过库存
            {"customer": "Eve", "town": "Ashland", "item": "AirPods Pro 3", "quantity": 2}
        ]
    }
    with open("requests/customer_orders.json", "w") as f:
        json.dump(requests, f, indent=4)

    # 规则笔记：非结构化，包含陷阱
    rules = """
    Gary's Logistics Notes (DO NOT LOSE!):
    * Superior Town: Entry fee is $50. They take 8% sales tax on total revenue. 
    * Ashland: These guys are chill. Entry fee is $20, but they have a strict 'luxury tax' of 15% on any single item sold over $300.
    * Rice Lake: Flat fee of $100. No sales tax, but they only allow max 3 items per person.
    * General rule: I want at least 15% net profit margin per town or I'm not stopping there!
    """
    with open("town_rules/logistics_guide.txt", "w") as f:
        f.write(rules)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 税率变更：与第一轮冲突
    tax_updates = {
        "Ashland": {"luxury_tax": 0.20, "entry_fee": 30},
        "Superior": {"sales_tax": 0.10}
    }
    with open("updates/new_tax_updates.json", "w") as f:
        json.dump(tax_updates, f, indent=4)

    # 回收请求：引入新的逻辑维度（折旧率）
    trade_ins = [
        ["customer", "town", "item_returned", "condition", "original_value"],
        ["Frank", "Rice Lake", "Old iPad", "Good", "200"],
        ["Grace", "Superior", "Broken Drone", "Poor", "500"],
    ]
    # 规则：Good 回收价是 40%, Poor 是 10%，Gary 以后卖出能翻倍。
    with open("requests/trade_in_requests.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(trade_ins)

def build_turn_3():
    os.makedirs("emergency", exist_ok=True)
    
    # 资金限制：迫使 Agent 进行多目标优化（放弃利润低且成本高的路径）
    crunch = """
    BAD NEWS! 
    My available cash for town entry fees and operations has been slashed to $120 total.
    You need to recalculate. Look at the entry fees from my first note and the updates. 
    Drop the two towns that make the least sense financially given this $120 cap.
    """
    with open("emergency/financial_crunch.txt", "w") as f:
        f.write(crunch)

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
