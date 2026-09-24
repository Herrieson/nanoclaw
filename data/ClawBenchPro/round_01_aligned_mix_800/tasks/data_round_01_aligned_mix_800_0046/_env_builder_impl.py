import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("raw_materials", exist_ok=True)
    os.makedirs("raw_materials/catering_options", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 志愿者白名单
    whitelist = ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Evan Wright"]
    with open("raw_materials/active_whitelist.txt", "w") as f:
        f.write("\n".join(whitelist))
        
    # 志愿者工时（含脏数据和超时数据）
    # Alice: 8h (超标), Bob: 4h (合规), Charlie: 5h (合规), Eve: 10h (不在白名单)
    volunteer_data = [
        ["name", "date", "hours"],
        ["Alice Smith", "2023-10-01", "8"],
        ["Bob Jones", "2023-10-01", "4"],
        ["Charlie Brown", "2023-10-02", "5"],
        ["Eve Malicious", "2023-10-02", "10"],
        ["Diana Prince", "2023-10-03", "2"]
    ]
    with open("raw_materials/volunteer_logs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(volunteer_data)

    # 供应商选项 (复杂逻辑：价格与风味的权衡)
    vendors = {
        "Savannah_Bistro": {"price": 1200, "flavors": ["African", "Spicy"], "items": ["Jollof Rice", "Suya"]},
        "Tribal_Grill": {"price": 1500, "flavors": ["Native American", "Smoked"], "items": ["Pemmican", "Frybread"]},
        "Global_Delights": {"price": 2500, "flavors": ["African", "Native American", "Caribbean"], "items": ["Couscous", "Bison Stew"]},
        "Cheap_Eats": {"price": 800, "flavors": ["Fast Food"], "items": ["Burgers"]}
    }
    for name, info in vendors.items():
        with open(f"raw_materials/catering_options/{name}.json", "w") as f:
            json.dump(info, f)

def build_turn_2():
    # 增加新志愿者数据
    os.makedirs("new_batch", exist_ok=True)
    os.makedirs("menu_details", exist_ok=True)
    
    # 紧急志愿者数据 (含冲突)
    emergency = [
        {"name": "Evan Wright", "date": "2023-10-05", "hours": 7}, # 需砍至6
        {"name": "Frank Castle", "date": "2023-10-05", "hours": 3}  # 不在白名单
    ]
    with open("new_batch/emergency_volunteers.json", "w") as f:
        json.dump(emergency, f)
        
    # 黑名单成分 (过敏原)
    with open("blacklisted_ingredients.txt", "w") as f:
        f.write("Peanuts\nShellfish\n")
        
    # 菜单明细 (决定供应商是否合规)
    # 假设 Global_Delights 有 Peanuts
    menu_details = {
        "Savannah_Bistro": "Ingredients: Rice, Tomato, Beef, Chili.",
        "Tribal_Grill": "Ingredients: Bison, Corn, Sage.",
        "Global_Delights": "Ingredients: Wheat, Peanuts, Lamb, Spices." 
    }
    for v, desc in menu_details.items():
        with open(f"menu_details/{v}_info.txt", "w") as f:
            f.write(desc)

def build_turn_3():
    # 最后一轮主要是汇总，不需要新的复杂文件结构
    os.makedirs("final_audit", exist_ok=True)

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
