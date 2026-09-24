import os
import argparse
import json
import csv
import random

def build_turn_1():
    # 创建目录结构
    os.makedirs("facility_ops/raw_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 区域协议：定义信用分要求和清洁难度
    zone_protocols = {
        "Casino_Floor": {"min_credit_score": 85, "priority": 10, "hazard_level": "High"},
        "VIP_Lounge": {"min_credit_score": 90, "priority": 9, "hazard_level": "Low"},
        "Theater_District": {"min_credit_score": 60, "priority": 7, "hazard_level": "Medium"},
        "Food_Court": {"min_credit_score": 40, "priority": 8, "hazard_level": "High"},
        "Employee_Locker_Rooms": {"min_credit_score": 0, "priority": 2, "hazard_level": "Low"}
    }
    with open("facility_ops/raw_data/zone_protocols.json", "w") as f:
        json.dump(zone_protocols, f, indent=4)

    # 2. 员工名单：故意制造一些违规项
    staff_data = [
        ["staff_id", "name", "credit_score", "assigned_zone", "hourly_rate"],
        ["S001", "Alice", 95, "VIP_Lounge", 25],
        ["S002", "Bob", 45, "Casino_Floor", 18],  # 违规：信用分不足
        ["S003", "Charlie", 70, "Theater_District", 20],
        ["S004", "David", 30, "Food_Court", 15],
        ["S005", "Eve", 88, "Casino_Floor", 22],
        ["S006", "Frank", 10, "Employee_Locker_Rooms", 12]
    ]
    with open("facility_ops/raw_data/staff_roster.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(staff_data)

def build_turn_2():
    # 模拟增量更新
    os.makedirs("new_hires", exist_ok=True)
    
    # 新增员工，其中有人信用分很高但薪资很高（测试预算意识），有人信用分极低
    new_hires = [
        {"staff_id": "S007", "name": "Grace", "credit_score": 92, "hourly_rate": 45}, # 贵但合规
        {"staff_id": "S008", "name": "Heidi", "credit_score": 35, "hourly_rate": 14}  # 便宜但不合规
    ]
    with open("new_hires/updates.json", "w") as f:
        json.dump(new_hires, f, indent=4)
    
    # 注入突发环境变化描述
    with open("facility_ops/raw_data/emergency_alert.txt", "w") as f:
        f.write("ALERT: Main pipe burst in Theater_District. Cleaning priority boosted to 11. Resource redirection required.")

def build_turn_3():
    os.makedirs("incident_reports", exist_ok=True)
    
    # 违规报告：在第二轮调整后发生的真实冲突
    # 假设 Agent 在第二轮为了补 Theater 的缺口，可能错误地调动了低信用分的人
    incidents = [
        {"timestamp": "2023-10-27 02:00", "location": "Casino_Floor", "detected_staff": "S008", "event": "Unauthorized Access"},
        {"timestamp": "2023-10-27 04:30", "location": "VIP_Lounge", "detected_staff": "S003", "event": "Tailgating observed"}
    ]
    with open("incident_reports/security_logs.json", "w") as f:
        json.dump(incidents, f, indent=4)

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
