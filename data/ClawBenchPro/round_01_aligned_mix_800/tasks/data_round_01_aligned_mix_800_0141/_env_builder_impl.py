import os
import argparse
import csv
import json

def build_turn_1():
    # 创建项目支出数据
    os.makedirs("projects", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)
    
    # 项目1: 预算 1,000,000, 支出 1,160,000 (超支16%，应冻结)
    # 项目2: 预算 500,000, 支出 520,000 (正常)
    # 项目3: 预算 2,000,000, 支出 2,100,000 (正常)
    
    project_data = {
        "P001_Skyline_Tower": [
            {"item": "Steel", "cost": 600000, "vendor": "V001"},
            {"item": "Concrete", "cost": 560000, "vendor": "V002"}
        ],
        "P002_Bridge_Repair": [
            {"item": "Labor", "cost": 300000, "vendor": "V003"},
            {"item": "Materials", "cost": 220000, "vendor": "V004"}
        ],
        "P003_Westside_Mall": [
            {"item": "Planning", "cost": 1000000, "vendor": "V005"},
            {"item": "Foundation", "cost": 1100000, "vendor": "V001"} # 潜在重复报销嫌疑项
        ]
    }
    
    for proj, items in project_data.items():
        with open(f"projects/{proj}.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["item", "cost", "vendor"])
            writer.writeheader()
            writer.writerows(items)

    # 初始预算表
    with open("initial_budgets.json", "w") as f:
        json.dump({
            "P001_Skyline_Tower": 1000000,
            "P002_Bridge_Repair": 500000,
            "P003_Westside_Mall": 2000000
        }, f)

    # 分包商注册表
    with open("vendor_registry.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["vendor_id", "name", "status"])
        writer.writeheader()
        writer.writerows([
            {"vendor_id": "V001", "name": "Global Steel Co", "status": "Active"},
            {"vendor_id": "V002", "name": "BuildRight Inc", "status": "Active"},
            {"vendor_id": "V003", "name": "Staffing Pros", "status": "Active"},
            {"vendor_id": "V004", "name": "Materials Plus", "status": "Active"},
            {"vendor_id": "V005", "name": "City Design", "status": "Active"}
        ])

def build_turn_2():
    # 动态注入增量数据
    os.makedirs("new_updates", exist_ok=True)
    
    # 黑名单信息
    with open("new_updates/blacklist_update.txt", "w") as f:
        f.write("URGENT: V001 (Global Steel Co) has been flagged for fraudulent billing in other regions. STOP ALL PAYMENTS.\n")
        f.write("Price Warning: Concrete prices from V002 are increasing by 25% effective immediately.")

    # 模拟项目4的数据突然出现
    with open("projects/P004_North_Tunnel.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["item", "cost", "vendor"])
        writer.writeheader()
        writer.writerows([
            {"item": "Excavation", "cost": 800000, "vendor": "V004"}
        ])
    
    with open("initial_budgets.json", "r") as f:
        budgets = json.load(f)
    budgets["P004_North_Tunnel"] = 900000
    with open("initial_budgets.json", "w") as f:
        json.dump(budgets, f)

def build_turn_3():
    # 重分配候选列表
    with open("reallocation_candidates.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["project_id", "priority", "current_efficiency"])
        writer.writeheader()
        writer.writerows([
            {"project_id": "P002_Bridge_Repair", "priority": "High", "current_efficiency": "0.95"},
            {"project_id": "P003_Westside_Mall", "priority": "Medium", "current_efficiency": "0.82"},
            {"project_id": "P004_North_Tunnel", "priority": "High", "current_efficiency": "0.98"}
        ])

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
