import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟原始库存日志
    os.makedirs("inventory_logs", exist_ok=True)
    inventory_data = [
        ["sku", "expected_qty", "actual_scan", "unit_price"],
        ["SKU_X_9921", "50", "48", "1200"],  # 缺失2个，高价值
        ["SKU_Y_1024", "100", "99", "450"],   # 缺失1个，低价值
        ["SKU_Z_5566", "20", "20", "3000"],  # 正常
        ["SKU_A_007", "15", "10", "800"],    # 缺失5个，高价值，且差异率大
        ["SKU_B_888", "200", "198", "50"]    # 缺失2个，低价值
    ]
    with open("inventory_logs/warehouse_a_scan.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # 模拟门禁日志
    os.makedirs("access_control", exist_ok=True)
    with open("access_control/door_logs.txt", "w") as f:
        f.write("2023-10-01 08:00:00 - Staff_001 - ENTRY\n")
        f.write("2023-10-01 22:30:00 - Staff_002 - ENTRY (Alert: Off-hours)\n")
        f.write("2023-10-02 03:15:00 - Staff_001 - ENTRY (Alert: Off-hours)\n")

    # 模拟排班表
    staff_data = [
        ["staff_id", "name", "shift_start", "shift_end"],
        ["Staff_001", "Marcus", "08:00", "17:00"],
        ["Staff_002", "Darnell", "09:00", "18:00"]
    ]
    with open("staff_schedules.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(staff_data)

def build_turn_2():
    # 供应商反驳数据
    os.makedirs("vendor_disputes", exist_ok=True)
    rebuttal = {
        "disputes": [
            {"sku": "SKU_X_9921", "reason": "Courier damage, not our responsibility", "admitted_loss": 0},
            {"sku": "SKU_A_007", "reason": "Short shipment acknowledged", "admitted_loss": 2}
        ]
    }
    with open("vendor_disputes/rebuttal.json", "w") as f:
        json.dump(rebuttal, f)

    # 员工解释
    os.makedirs("staff_excuses", exist_ok=True)
    with open("staff_excuses/staff_001_statement.txt", "w") as f:
        f.write("I came back at 03:15 AM because I forgot my house keys in the locker. I didn't touch the inventory.")

def build_turn_3():
    # 总部新政策
    os.makedirs("hq_updates", exist_ok=True)
    with open("hq_updates/new_policy.pdf", "w") as f:
        f.write("POLICY UPDATE v2.1:\n")
        f.write("1. High-Value Threshold: Any item > $400 (Previously was $500).\n")
        f.write("2. Claim Calculation: Loss Amount = (Missing Qty * Unit Price) * 0.9 (Depreciation).\n")
        f.write("3. Fraud Zero Tolerance: Any off-hour entry without secondary witness must be flagged for termination.\n")

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
