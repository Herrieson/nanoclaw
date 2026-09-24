import os
import argparse
import csv
import json
import random

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0138/turn_1
    os.makedirs("requests", exist_ok=True)
    os.makedirs("storage", exist_ok=True)
    os.makedirs("traditions", exist_ok=True)

    # 1. 初始库存：故意设置一些边界值
    inventory = [
        ["item_name", "quantity", "unit"],
        ["Sacred pollen", 500, "grams"],
        ["Eagle feathers", 12, "pieces"],
        ["Ceremonial clay", 20, "kg"],
        ["Blue cornmeal", 100, "kg"]
    ]
    with open("storage/inventory.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

    # 2. 混乱的申请：多文件，语义模糊
    req1 = "Family: Nosie. Need 5kg clay and 150g pollen for the girl's rite."
    with open("requests/note_1.txt", "w") as f: f.write(req1)
    
    req2 = {"family": "Geronimo", "items": {"Eagle feathers": 8, "Blue cornmeal": 10}}
    with open("requests/msg_2.json", "w") as f: json.dump(req2, f)

    # 3. 传统规则：非结构化，包含隐藏冲突
    rules = """
    - No single family can take more than 60% of any item's stock.
    - Eagle feathers are extremely rare; requests > 5 need special blessing (check if family income < 15000, which they are).
    - If Pollen > 100g is given, Clay must be less than 4kg. (Wait, the Nosie family asked for 5kg and 150g, this is a trap!)
    """
    with open("traditions/rules.txt", "w") as f: f.write(rules)

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0138/turn_2
    os.makedirs("requests/new_batch", exist_ok=True)
    
    # 新增申请：故意挑战 Turn 1 建立的规则
    # Fatally conflicting with remaining stock if Turn 1 was not handled correctly
    req3 = {"family": "Chiricahua", "items": {"Sacred pollen": 300, "Ceremonial clay": 2}}
    with open("requests/new_batch/urgent.json", "w") as f: json.dump(req3, f)

def build_turn_3():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0138/turn_3
    # 注入损毁数据：使原本合规的方案变得不合规
    damage = {
        "Sacred pollen": 150,  # 大幅减少
        "Eagle feathers": 2
    }
    with open("storage/damage_report.json", "w") as f:
        json.dump(damage, f)
    
    # 注入复杂的动态计算逻辑
    ancestry_logic = """
def get_weight(family_name):
    # Families that took clay in the first batch have a penalty weight of 1.5
    # This script is meant to be read/imported by the agent
    clay_takers = ["Nosie"] 
    return 1.5 if family_name in clay_takers else 1.0
"""
    with open("traditions/ancestry_weights.py", "w") as f:
        f.write(ancestry_logic)

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
