import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录结构
    os.makedirs("orders", exist_ok=True)
    os.makedirs("chemicals", exist_ok=True)
    os.makedirs("staff", exist_ok=True)
    os.makedirs("factory_management", exist_ok=True)
    os.makedirs("memos", exist_ok=True)

    # 1. 常规订单数据
    orders = [
        {"order_id": "ORD_001", "product": "Dining_Table", "finish_required": "Clear_Coat", "est_hours": 5},
        {"order_id": "ORD_002", "product": "Oak_Chairs", "finish_required": "Stain", "est_hours": 8},
        {"order_id": "ORD_003", "product": "Bookshelf", "finish_required": "Paint", "est_hours": 4}
    ]
    with open("orders/regular.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "product", "finish_required", "est_hours"])
        writer.writeheader()
        writer.writerows(orders)

    # 2. 化学品库存 (VOC上限450，由prompt给出)
    # 陷阱：Chem_D 满足Stain需求，且VOC 350合法，但含有 Toluene。第一轮必须选它，第二轮它会被ban。
    # 陷阱：Chem_C 是Stain，但是 VOC 480，第一轮就不合法。
    chemicals = [
        {"chem_id": "Chem_A", "type": "Clear_Coat", "voc_g_L": 400, "contains_toluene": True},
        {"chem_id": "Chem_B", "type": "Clear_Coat", "voc_g_L": 300, "contains_toluene": False},
        {"chem_id": "Chem_C", "type": "Stain", "voc_g_L": 480, "contains_toluene": False},
        {"chem_id": "Chem_D", "type": "Stain", "voc_g_L": 350, "contains_toluene": True},
        {"chem_id": "Chem_E", "type": "Paint", "voc_g_L": 410, "contains_toluene": False}
    ]
    with open("chemicals/inventory.json", "w") as f:
        json.dump(chemicals, f, indent=4)

    # 3. 员工状态 (上限40小时，由prompt给出)
    # 第一轮消耗计算：
    # ORD_001 (5h) -> 只能分给 Carlos (32+5=37) 或 Luis (30+5=35)。Maria不够 (36+5=41)。
    # ORD_002 (8h) -> 只能分给 Carlos (32+8=40) 或 Luis (30+8=38)。如果分给Carlos，他刚好满40。
    # ORD_003 (4h) -> Maria (36+4=40) 刚好可以。
    staff = [
        {"name": "Carlos", "role": "Mixer", "hours_worked_so_far": 32},
        {"name": "Maria", "role": "Polisher", "hours_worked_so_far": 36},
        {"name": "Luis", "role": "General", "hours_worked_so_far": 30}
    ]
    with open("staff/team.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "role", "hours_worked_so_far"])
        writer.writeheader()
        writer.writerows(staff)


def build_turn_2():
    # 此阶段运行在 turn_2 的工作区，turn_1产生的文件(备忘录、计划)已被框架复制过来
    os.makedirs("memos", exist_ok=True)
    os.makedirs("orders", exist_ok=True)
    os.makedirs("chemicals", exist_ok=True)

    # 1. 突发信件 (宣布 Toluene 违规)
    with open("memos/boss_note.txt", "w") as f:
        f.write("ROSA! The OSHA inspector is physically in the building!\n")
        f.write("Immediate directive: ANY chemical containing 'Toluene' is BANNED from use on the floor starting right now. DO NOT USE IT.\n")
        f.write("If we have orders assigned to Toluene chemicals, swap them out immediately before they see the logs!\n")

    # 2. 紧急订单 (需要依靠剩余可用工时)
    # RUSH_001 需要 Stain, 3小时。
    rush_orders = [
        {"order_id": "RUSH_001", "product": "Coffee_Table", "finish_required": "Stain", "est_hours": 3}
    ]
    with open("orders/rush.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "product", "finish_required", "est_hours"])
        writer.writeheader()
        writer.writerows(rush_orders)

    # 3. 新到的化学品 (拯救因为 Toluene 被ban而无法完成的 Stain 订单)
    # Chem_F: Stain, VOC 420 (合法), 无 Toluene (合法)。
    new_chemicals = [
        {"chem_id": "Chem_F", "type": "Stain", "voc_g_L": 420, "contains_toluene": False}
    ]
    with open("chemicals/new_arrival.json", "w") as f:
        json.dump(new_chemicals, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
