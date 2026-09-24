import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟物理治疗师的杂乱工作环境
    os.makedirs("clinic_schedules", exist_ok=True)
    os.makedirs("procurement", exist_ok=True)
    
    # 1. 诊所排班数据 (包含违规项)
    # Bluegrass: 某人单日超过8小时，且周中有一天没有资深治疗师
    schedules = [
        {"Name": "Alice (Senior)", "Mon": 9, "Tue": 9, "Wed": 9, "Thu": 9, "Fri": 4}, # Over 8h
        {"Name": "Bob (Junior)", "Mon": 8, "Tue": 8, "Wed": 8, "Thu": 8, "Fri": 8},   # OK
        {"Name": "Charlie (Junior)", "Mon": 4, "Tue": 0, "Wed": 0, "Thu": 4, "Fri": 4} # Wed no senior if others missing
    ]
    with open("clinic_schedules/bluegrass_q4.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=schedules[0].keys())
        writer.writeheader()
        writer.writerows(schedules)

    # 2. 采购数据 (埋伏笔：Vertex Corp 此时看起来性价比最高)
    procurement_data = [
        ["ID", "Item", "Category", "Supplier", "Price", "Rating", "Self_Care_Score"],
        ["P001", "Therapy Ball", "Basic", "Vertex Corp", 120, 4.8, 9],
        ["P002", "Electric Treatment Table", "Equipment", "MediGear", 5500, 4.5, 3], # Price too high > 5000
        ["P003", "Resistance Band Set", "Self-Care", "Vertex Corp", 45, 4.2, 10],
        ["P004", "Home Traction Unit", "Self-Care", "HealthLink", 4800, 4.1, 8],
        ["P005", "Low-Quality Mat", "Basic", "BudgetFit", 30, 3.5, 2], # Rating < 4.0
        ["P006", "Ultrasound Machine", "Advanced", "MediGear", 4200, 4.6, 5],
        ["P007", "Massage Chair", "Luxury", "Vertex Corp", 6000, 4.9, 7], # Price > 5000
    ]
    with open("procurement/pending_requests.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(procurement_data)

def build_turn_2():
    # 动态注入新政策和反馈
    os.makedirs("updates", exist_ok=True)
    with open("updates/memo_new_policy.txt", "w") as f:
        f.write("URGENT: Effective immediately, all contracts with Vertex Corp are suspended due to compliance violations. Do not authorize payments.")
    
    # 增加排班复杂性：跨院区冲突
    feedback = {
        "conflicts": [
            {"staff": "Bob (Junior)", "issue": "Scheduled in Bluegrass and Derby on the same Tuesday morning."},
            {"staff": "Alice (Senior)", "issue": "Requested Wed off for yoga retreat."}
        ]
    }
    with open("clinic_schedules/feedback_turn2.json", "w") as f:
        json.dump(feedback, f)

def build_turn_3():
    # 注入家庭数据
    os.makedirs("patient_data", exist_ok=True)
    patients = [
        {"FamilyID": "F01", "Condition": "Post-Op Knee", "Required_Kit": "Self-Care"},
        {"FamilyID": "F02", "Condition": "Chronic Back Pain", "Required_Kit": "Self-Care"},
        {"FamilyID": "F03", "Condition": "Shoulder Rehab", "Required_Kit": "Basic"}
    ]
    with open("patient_data/eligible_families.json", "w") as f:
        json.dump(patients, f)

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
