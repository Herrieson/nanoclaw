import os
import argparse
import json
import random

def build_turn_1():
    # 建立初始行政环境
    os.makedirs("incident_logs", exist_ok=True)
    os.makedirs("personnel", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    
    # 警员名单与状态，包含极其复杂的排班偏好与工会规则冲突
    officers = [
        {"id": "PO-101", "name": "Garcia", "rank": "Senior", "shift_preference": "Night", "hourly_rate": 65, "extra_skills": ["Spanish-Fluent", "Crisis-Negotiation"]},
        {"id": "PO-102", "name": "O'Malley", "rank": "Junior", "shift_preference": "Day", "hourly_rate": 45, "extra_skills": []},
        {"id": "PO-103", "name": "Chen", "rank": "Senior", "shift_preference": "Day", "hourly_rate": 68, "extra_skills": ["Forensics"]},
        {"id": "PO-104", "name": "Smith", "rank": "Mid", "shift_preference": "Night", "hourly_rate": 55, "extra_skills": ["K9-Unit"]},
    ]
    with open("personnel/active_roster.json", "w") as f:
        json.dump(officers, f)

    # 包含脏数据的巡逻车日志
    vehicle_logs = [
        "DATE,UNIT_ID,MILEAGE_START,MILEAGE_END,FUEL_LEVEL,ISSUE_REPORTED",
        "2023-10-01,V-99,120500,120650,45%,None",
        "2023-10-01,V-42,45000,45120,80%,Brakes squeaking",
        "2023-10-02,V-99,120650,ERROR_CODE_X,30%,Check Engine", # 脏数据
        "2023-10-02,V-42,45120,45300,10%,Flat tire",
        "2023-10-03,V-99,120650,120800,20%,Severe transmission slip" # 里程回退错误
    ]
    with open("inventory/patrol_vehicles.csv", "w") as f:
        f.write("\n".join(vehicle_logs))

    # 复杂规则说明：州政府年度预算剩余与加班限制（文字描述）
    regulations = """
    DEPARTMENTAL DIRECTIVE 2023-04:
    1. Total remaining overtime budget for Q4: $12,500. 
    2. Overtime is calculated as 1.5x hourly rate after 8 hours in a 24h window.
    3. Vehicles with mileage over 120,000 must undergo Level 2 Inspection before any pursuit-grade missions.
    4. Junior officers (Rank: Junior) must never be paired together on Night shifts.
    """
    with open("internal_policy.txt", "w") as f:
        f.write(regulations)

def build_turn_2():
    # 增加新的冲突：紧急调配与预算变动
    os.makedirs("emergency_orders", exist_ok=True)
    new_task = {
        "event": "Public Demonstration Support",
        "date": "2023-10-15",
        "required_officers": 3,
        "special_requirement": "Bilingual-Spanish Preferred",
        "est_duration_hours": 12
    }
    with open("emergency_orders/demo_task.json", "w") as f:
        json.dump(new_task, f)

def build_turn_3():
    # 第三轮：设备彻底报废导致的连带责任分析
    # 此时 Agent 应该已经记录了 V-99 的问题
    with open("incident_logs/incident_report_1016.txt", "w") as f:
        f.write("OFFICER: O'Malley. VEHICLE: V-99. STATUS: Total Loss. ACCIDENT: Transmission failure during routine patrol. Budget for new vehicle replacement needed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1: build_turn_1()
    elif args.turn == 2: build_turn_2()
    elif args.turn == 3: build_turn_3()
