import os
import argparse
import csv
import json
import random

def build_turn_1():
    # 创建基础目录
    os.makedirs("incoming_proposals", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 供应商元数据：环保得分陷阱
    # 供应商 C 看起来最完美，但刚好 7.4 分（低于红线 7.5）
    vendors = [
        ["Vendor_A", 8.2, "7 days", "High-End"],
        ["Vendor_B", 7.6, "14 days", "Minimalist"],
        ["Vendor_C", 7.4, "5 days", "Eco-Luxury"], # Trap: High score but below 7.5
        ["Vendor_D", 9.1, "21 days", "Sporty"],
        ["Vendor_E", 7.8, "10 days", "Classic"]
    ]
    with open("vendor_metadata.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["VendorName", "SustainabilityScore", "LeadTime", "Style"])
        writer.writerows(vendors)

    # 报价单数据
    proposals = {
        "Vendor_A": {"unit_cost": 120, "min_order": 200, "renovation_fee": 20000},
        "Vendor_B": {"unit_cost": 85, "min_order": 300, "renovation_fee": 15000},
        "Vendor_C": {"unit_cost": 90, "min_order": 250, "renovation_fee": 12000},
        "Vendor_D": {"unit_cost": 150, "min_order": 100, "renovation_fee": 25000},
        "Vendor_E": {"unit_cost": 95, "min_order": 200, "renovation_fee": 18000}
    }
    for v, data in proposals.items():
        with open(f"incoming_proposals/{v}_quote.json", "w") as f:
            json.dump(data, f)

def build_turn_2():
    # 模拟 turn_1 已经执行，现在在 turn_2 的工作区
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    
    # 物流延迟陷阱：Vendor_D (得分最高者) 严重延迟
    delays = {
        "Vendor_A": "On Time",
        "Vendor_B": "3 days delay",
        "Vendor_D": "Indefinite delay due to customs", # Trap
        "Vendor_E": "On Time"
    }
    with open("logistics/delays.json", "w") as f:
        json.dump(delays, f)
    
    # 现有库存 (需要 Openpyxl 的模拟，这里用 csv 替代方便处理)
    inventory = [
        ["Store", "Brand", "CurrentStock", "TargetStock"],
        ["North", "Classic", 50, 200],
        ["North", "Minimalist", 20, 150],
        ["South", "High-End", 10, 100],
        ["South", "Classic", 40, 200],
        ["Central", "Minimalist", 30, 180],
        ["Central", "High-End", 5, 120]
    ]
    with open("inventory/current_stock.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

def build_turn_3():
    os.makedirs("display_specs", exist_ok=True)
    os.makedirs("item_specs", exist_ok=True)
    
    # 店面布局限制
    layouts = """<layouts>
    <store id="North" capacity_kg="500" shelf_count="10" />
    <store id="South" capacity_kg="300" shelf_count="6" />
    <store id="Central" capacity_kg="800" shelf_count="15" />
</layouts>"""
    with open("display_specs/layouts.xml", "w") as f:
        f.write(layouts)
    
    # 重量数据：环保材料通常较重
    weights = {
        "High-End": 0.45, # kg per unit
        "Minimalist": 0.25,
        "Classic": 0.35,
        "Sporty": 0.55
    }
    with open("item_specs/weights.json", "w") as f:
        json.dump(weights, f)
        
    # 装饰费
    with open("display_specs/costs.conf", "w") as f:
        f.write("basic_decoration_per_store=5000\npremium_signage_package=8500")

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
