import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0146/turn_1
    os.makedirs("inventory/incoming", exist_ok=True)
    os.makedirs("specs", exist_ok=True)
    
    # 供应商清单 1：正常数据
    with open("inventory/incoming/supplier_a.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "model", "price", "emission_tag"])
        writer.writerow(["A001", "Excavator-X", "5000", "Tier-3"]) # 合规
        writer.writerow(["A002", "Loader-L1", "14000", "Tier-2"])  # 排放不合规
        writer.writerow(["A003", "Crane-C9", "19000", "Tier-3"])   # 价格超标

    # 供应商清单 2：带乱码/隐蔽数据 (需查找 lookup)
    with open("inventory/incoming/supplier_b.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "model", "price", "emission_tag"])
        writer.writerow(["B001", "Drill-D2", "8000", "UNKNOWN"]) # 需要查表，对应 Tier-3
        writer.writerow(["B002", "Pump-P5", "12000", "UNKNOWN"]) # 需要查表，对应 Tier-1

    # 供应商清单 3：脏数据
    with open("inventory/incoming/supplier_c.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "model", "price", "emission_tag"])
        writer.writerow(["C001", "Forklift-F", "17500", "Tier-3"]) # 合规，但总额极高

    # 效率映射表
    lookup = {
        "Drill-D2": "Tier-3",
        "Pump-P5": "Tier-1",
        "Excavator-X": "Tier-3"
    }
    with open("specs/efficiency_lookup.json", "w") as f:
        json.dump(lookup, f)

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0146/turn_2
    os.makedirs("compliance", exist_ok=True)
    os.makedirs("inventory/emergency_batch", exist_ok=True)

    # 新协议：除了 Tier-3，还必须满足能耗等级 (E-Rating) 必须为 A 或 B
    with open("compliance/new_protocol.txt", "w") as f:
        f.write("Update: Green-Horizon-2024 Protocol\n")
        f.write("All previously approved Tier-3 items must also have an E-Rating of A or B.\n")
        f.write("Items with E-Rating C are now strictly prohibited regardless of price.\n")

    # 紧急调拨批次：毒药选项
    # 这里的 D001 在第一轮标准下是完美的，但在第二轮标准下因为 E-Rating 会挂掉
    with open("inventory/emergency_batch/urgent.json", "w") as f:
        json.dump([
            {"item_id": "D001", "model": "Generator-G1", "price": 15000, "emission_tag": "Tier-3", "e_rating": "C"},
            {"item_id": "D002", "model": "Mixer-M7", "price": 2000, "emission_tag": "Tier-3", "e_rating": "A"}
        ], f)
    
    # 同时也更新原有的 lookup，增加 E-Rating 信息，逼迫 Agent 重新关联
    lookup_v2 = {
        "A001": "B",
        "B001": "C", # 原本第一轮合规的 B001，现在因为 E-Rating C 不合规了
        "C001": "A",
        "D001": "C",
        "D002": "A"
    }
    with open("specs/efficiency_lookup.json", "w") as f:
        json.dump(lookup_v2, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
