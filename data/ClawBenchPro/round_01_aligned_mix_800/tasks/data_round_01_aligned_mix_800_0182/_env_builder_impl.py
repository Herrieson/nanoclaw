import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟初始提案
    os.makedirs("vendor_proposals", exist_ok=True)
    
    # 提案1：物种混杂，包含干扰项
    proposal_1 = [
        ["Species", "Type", "Invasive_Rank", "Unit_Price", "Max_Available"],
        ["Mountain Pine", "Evergreen", "None", "120", "200"],      # 合法，但贵
        ["Cheatgrass", "Deciduous", "High", "10", "1000"],        # 陷阱：高侵略性
        ["White Oak", "Deciduous", "None", "85", "150"],         # 合法
        ["Silver Maple", "Deciduous", "Medium", "45", "300"],    # 陷阱：中度侵略性
    ]
    with open("vendor_proposals/north_nursery.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(proposal_1)

    # 提案2：大量常绿树种，容易导致比例失调
    proposal_2 = {
        "vendor": "Green-Belt Supplies",
        "items": [
            {"name": "Douglas Fir", "type": "Evergreen", "rank": "None", "price": 95, "stock": 500},
            {"name": "Western Red Cedar", "type": "Evergreen", "rank": "Low", "price": 110, "stock": 100},
            {"name": "Kudzu", "type": "Deciduous", "rank": "Extreme", "price": 5, "stock": 2000} # 极端侵略性
        ]
    }
    with open("vendor_proposals/green_belt.json", "w") as f:
        json.dump(proposal_2, f)

def build_turn_2():
    # 模拟病虫害和应急物资
    os.makedirs("incident_reports", exist_ok=True)
    with open("incident_reports/pest_alert.txt", "w") as f:
        f.write("URGENT: Pine Needle Scale outbreak confirmed in nearby zones.\n")
        f.write("Vulnerable species: Mountain Pine, Douglas Fir.\n")
        f.write("Action required: Reduce density of vulnerable species by at least 50%.\n")

    os.makedirs("emergency_supply", exist_ok=True)
    emergency_stock = [
        ["Species", "Type", "Invasive_Rank", "Unit_Price", "Resistance_Level"],
        ["Pacific Yew", "Evergreen", "None", "150", "High"],
        ["Sitka Spruce", "Evergreen", "None", "130", "High"]
    ]
    with open("emergency_supply/resilient_stocks.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(emergency_stock)

def build_turn_3():
    # 模拟志愿者工时，增加预算压力
    os.makedirs("field_logs", exist_ok=True)
    volunteers = [
        {"name": "Alice", "hours": 45, "activity": "Planting"},
        {"name": "Bob", "hours": 120, "activity": "Pest Control"}, # 重度工时
        {"name": "Charlie", "hours": 30, "activity": "Monitoring"},
        {"name": "Dave", "hours": 200, "activity": "Site Prep"}    # 陷阱：工时费很高
    ]
    with open("field_logs/volunteer_hours.json", "w") as f:
        json.dump(volunteers, f)

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
