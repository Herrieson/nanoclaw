import os
import argparse
import json
import csv

def build_turn_1():
    # 建立初始混乱环境
    os.makedirs("inbox/raw_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商数据 - 故意设计冲突和脏数据
    suppliers = [
        ["name", "category", "price", "specs", "date"],
        ["SonicBoom", "audio", "8500", "SNR: 95dB", "2023-10-01"],
        ["EcoGlass", "glass_sponsor", "-2000", "Tier 1", "2023-10-05"], # 负数代表赞助费
        ["AudioVisual_Pro", "audio", "7200", "SNR: 88dB", "2023-09-20"],
        ["GlassEmpire", "glass_sponsor", "-1500", "Tier 2", "2023-10-02"],
        ["SecurityGuard_Inc", "security", "1500", "per_person", "2023-10-01"]
    ]
    with open("inbox/raw_data/suppliers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(suppliers)

    # 场地要求
    with open("venue_specs.txt", "w") as f:
        f.write("Venue: Riverside Warehouse\n")
        f.write("Requirement: Audio Signal-to-Noise Ratio (SNR) must be > 90dB to overcome industrial noise.\n")
        f.write("Max Occupancy: 200\n")

    # 干扰项：一封过时的报价邮件
    with open("inbox/raw_data/email_draft.txt", "w") as f:
        f.write("From: SonicBoom\nDate: 2023-09-01\nOld price was 9500, please ignore the previous quote.")

def build_turn_2():
    # 模拟 Turn 2 的增量变更
    os.makedirs("updates", exist_ok=True)
    
    # 新赞助商进入，带有排他性条款
    update_data = {
        "new_sponsor": "CrystalClear Glass",
        "offer_amount": 5000,
        "conditions": ["Exclusive branding", "No other glass logos"],
        "cancellation_fee_policy": 0.2 # 取消其他供应商需支付20%违约金
    }
    with open("updates/sponsor_offer.json", "w") as f:
        json.dump(update_data, f, indent=4)

def build_turn_3():
    # 模拟 Turn 3 的资源冲突
    # 员工排班
    staff_shifts = {
        "total_staff": 8,
        "event_setup_required": 4,
        "repair_skill_level": "High"
    }
    with open("staff_shifts.json", "w") as f:
        json.dump(staff_shifts, f, indent=4)

    # 维修单
    conflicts = [
        ["task_id", "est_hours", "priority"],
        ["F150_001", "2.5", "Urgent"],
        ["F150_002", "3.0", "Normal"],
        ["F150_003", "2.0", "Urgent"],
        ["F150_004", "4.5", "Urgent"]
    ]
    with open("inventory_conflict.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(conflicts)

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
