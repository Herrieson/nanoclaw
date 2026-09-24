import os
import argparse
import json
import csv

def build_turn_1():
    # 创建目录结构
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("planning", exist_ok=True)
    
    # 初始供应商数据：包含陷阱（价格便宜但环保分低，或环保分高但距离远）
    initial_vendors = [
        {"id": "V001", "name": "Standard Plastic Co.", "item": "Trash Bags", "price": 100, "eco_score": 40, "distance_miles": 5, "material": "Plastic", "mwbe": False},
        {"id": "V002", "name": "GreenLife Bio", "item": "Trash Bags", "price": 140, "eco_score": 95, "distance_miles": 120, "material": "Bio-degradable", "mwbe": False},
        {"id": "V003", "name": "EcoWarrior Supplies", "item": "Gloves", "price": 200, "eco_score": 85, "distance_miles": 45, "material": "Latex", "mwbe": True},
        {"id": "V004", "name": "Local Tools", "item": "Grabbers", "price": 500, "eco_score": 75, "distance_miles": 2, "material": "Recycled Steel", "mwbe": False},
        {"id": "V005", "name": "Bulk-O-Mat", "item": "Grabbers", "price": 300, "eco_score": 30, "distance_miles": 10, "material": "Plastic/Aluminum", "mwbe": False}
    ]
    
    with open("vendors/initial_list.json", "w") as f:
        json.dump(initial_vendors, f, indent=4)

def build_turn_2():
    # 模拟 turn_2 的新增数据
    # 增加一个 MWBE 且环保分勉强达标但极贵的选项，看 Agent 怎么平衡
    new_proposals = [
        ["id", "name", "item", "price", "eco_score", "distance_miles", "material", "mwbe"],
        ["V006", "River Clean Tech", "Trash Bags", "125", "88", "10", "Bio-degradable", "True"],
        ["V007", "Big Corp Logistics", "Gloves", "150", "65", "80", "Nitrile", "False"],
        ["V008", "Unity Supplies", "Gloves", "220", "72", "15", "Bio-degradable", "True"]
    ]
    
    with open("vendors/new_proposals.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_proposals)

def build_turn_3():
    # 模拟 turn_3 的紧急变更
    os.makedirs("updates", exist_ok=True)
    with open("updates/emergency_notice.txt", "w") as f:
        f.write("URGENT NOTICE: Soil test results show high acidity levels at the river bank.\n")
        f.write("All protective gloves MUST be 'Acid-Resistant' and have a thickness rating > 5mm.\n")
        f.write("Note: Standard Bio-degradable latex (like V003/V008) will NOT suffice. Please check 'V009' from SpecialGear.\n")
    
    # 增加一个新的符合酸抗性的供应商
    new_vendor = {
        "id": "V009",
        "name": "SpecialGear Safety",
        "item": "Gloves",
        "price": 350, # 昂贵，迫使 Agent 调整其他预算
        "eco_score": 71,
        "distance_miles": 40,
        "material": "Acid-Resistant Eco-Polymer",
        "mwbe": True
    }
    
    # 将其注入到某个文件中
    with open("vendors/special_emergency.json", "w") as f:
        json.dump([new_vendor], f)

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
