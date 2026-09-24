import os
import argparse
import json
import random

def build_turn_1():
    # 建立病患数据
    os.makedirs("patient_data", exist_ok=True)
    patients = []
    sectors = ["Sector_A", "Sector_B", "Sector_C", "Sector_D"]
    for i in range(1, 21):
        level = random.randint(1, 5)
        sector = random.choice(sectors)
        # 陷阱：Sector_B 有几个高危病患，为第二轮封锁埋雷
        patients.append({
            "id": f"P-{i:03d}",
            "name": f"Elderly_{i}",
            "condition_level": level,
            "sector": sector,
            "monthly_cost": 200 + level * 100,
            "needs_medical_pro": level >= 4
        })
    with open("patient_data/records.json", "w") as f:
        json.dump(patients, f, indent=4)

    # 建立志愿者数据
    os.makedirs("volunteer_registry", exist_ok=True)
    volunteers = [
        {"id": "V-01", "name": "Alice", "has_medical_bg": True, "max_hours": 40, "base_sector": "Sector_A"},
        {"id": "V-02", "name": "Bob", "has_medical_bg": False, "max_hours": 30, "base_sector": "Sector_B"},
        {"id": "V-03", "name": "Charlie", "has_medical_bg": True, "max_hours": 20, "base_sector": "Sector_C"},
        {"id": "V-04", "name": "David", "has_medical_bg": False, "max_hours": 50, "base_sector": "Sector_D"},
        {"id": "V-05", "name": "Eve", "has_medical_bg": True, "max_hours": 35, "base_sector": "Sector_B"},
    ]
    with open("volunteer_registry/volunteers.json", "w") as f:
        json.dump(volunteers, f, indent=4)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 封锁信息
    lockdown = {"restricted_zone": "Sector_B", "status": "No_Entry", "reason": "Event_Traffic_Control"}
    with open("updates/traffic_update.json", "w") as f:
        json.dump(lockdown, f, indent=4)
    
    # 增加紧急病患
    new_patients = [
        {"id": "P-NEW-01", "name": "Emergency_Sarah", "condition_level": 5, "sector": "Sector_A", "monthly_cost": 800, "needs_medical_pro": True}
    ]
    with open("updates/emergency_list.csv", "w") as f:
        f.write("id,name,level,sector,cost,medical_required\n")
        for p in new_patients:
            f.write(f"{p['id']},{p['name']},{p['condition_level']},{p['sector']},{p['monthly_cost']},True\n")

def build_turn_3():
    os.makedirs("feedback_logs", exist_ok=True)
    # 志愿者反馈，包含部署陷阱
    feedbacks = [
        {"patient_id": "P-001", "tech_friendly": False, "comment": "No Wi-Fi available at home."},
        {"patient_id": "P-002", "tech_friendly": True, "comment": "Very interested in new gadgets."},
        {"patient_id": "P-005", "tech_friendly": False, "comment": "Patient suffers from severe dementia, cannot use devices."},
    ]
    # 为所有第一轮生成的病患随机生成一些干扰反馈
    for i in range(1, 21):
        pid = f"P-{i:03d}"
        if not any(f['patient_id'] == pid for f in feedbacks):
            feedbacks.append({"patient_id": pid, "tech_friendly": random.choice([True, True, False]), "comment": "Normal status."})
            
    with open("feedback_logs/volunteer_notes.json", "w") as f:
        json.dump(feedbacks, f, indent=4)

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
