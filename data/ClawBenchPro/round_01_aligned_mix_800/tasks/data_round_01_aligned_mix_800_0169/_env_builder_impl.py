import os
import argparse
import json
import csv
from datetime import datetime

def build_turn_1():
    # 建立目录结构
    os.makedirs("clinic_data", exist_ok=True)
    os.makedirs("patient_files", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 原始排班数据：在 Monday 10:00 AM 制造 4 人冲突 (只有3个房间)
    schedule = [
        {"patient_id": "P001", "time": "2023-10-23 10:00", "duration": "1h"},
        {"patient_id": "P002", "time": "2023-10-23 10:00", "duration": "1h"},
        {"patient_id": "P003", "time": "2023-10-23 10:00", "duration": "1h"},
        {"patient_id": "P004", "time": "2023-10-23 10:00", "duration": "1h"},
        {"patient_id": "P005", "time": "2023-10-23 11:00", "duration": "1h"},
    ]
    with open("clinic_data/schedule_raw.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["patient_id", "time", "duration"])
        writer.writeheader()
        writer.writerows(schedule)

    # 2. 患者档案：决定优先级 (入组日期越早越优先)
    # P004 是最早的，P001, P002 其次，P003 是最晚的（应该被踢到 waitlist）
    patients = [
        {"id": "P001", "name": "Alice", "joined": "2022-01-15"},
        {"id": "P002", "name": "Bob", "joined": "2022-03-20"},
        {"id": "P003", "name": "Charlie", "joined": "2023-05-01"},
        {"id": "P004", "name": "David", "joined": "2021-11-10"},
        {"id": "P005", "name": "Eve", "joined": "2022-06-01"},
    ]
    for p in patients:
        with open(f"patient_files/{p['id']}.json", "w") as f:
            json.dump(p, f)

    # 3. 供应商报价：陷阱设计
    # Supplier A: 价格便宜但不可回收
    # Supplier B: 价格 $14.5 (符合)，可回收 (符合) -> 预选目标
    # Supplier C: 价格 $18.0 (超标)，可回收
    bids = [
        {"name": "QuickMed", "item": "Sensory Ball", "price": 12.0, "recyclable": False},
        {"name": "EcoTherapy", "item": "Sensory Ball", "price": 14.5, "recyclable": True},
        {"name": "PremiumHealth", "item": "Sensory Ball", "price": 18.0, "recyclable": True}
    ]
    with open("suppliers/bids.json", "w") as f:
        json.dump(bids, f)

def build_turn_2():
    # 增加紧急转介数据
    # P006 加入，时间也是 10:00 AM，且 P006 入组日期极早 (2020年)，会挤掉现有的某人
    os.makedirs("clinic_data", exist_ok=True)
    referrals = [
        {"patient_id": "P006", "name": "Frank", "joined": "2020-05-12", "time": "2023-10-23 10:00", "duration": "1h"}
    ]
    with open("clinic_data/urgent_referrals.json", "w") as f:
        json.dump(referrals, f)
    
    # 模拟 Turn 1 选中的供应商 EcoTherapy 突然失效
    # Agent 必须看剩下的。此时只剩 A 和 C。
    # A 不合规（不可回收），C 不合规（超支）。
    # 这里是一个逻辑困境：Agent 应该在记录中寻找备选或报告无法采购。
    # 实际上，我们可以增加一个隐藏供应商文件
    with open("suppliers/last_minute_offer.txt", "w") as f:
        f.write("Backdoor Supplies: Sensory Ball - $14.99 - Recyclable: YES")

def build_turn_3():
    # 增加合规性更新文件
    os.makedirs("compliance", exist_ok=True)
    with open("compliance/emergency_update.txt", "w") as f:
        f.write("EMERGENCY COVID PROTOCOL: Room B must remain empty for ventilation every other hour. ")
        f.write("Specifically, no appointments allowed in Room B at 10:00 AM.")
    # 这将导致原本在 Room B 的 10:00 的预约（根据 Turn 1/2 逻辑排好的）必须再次移动。

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
