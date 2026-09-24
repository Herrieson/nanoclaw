import os
import argparse
import json
import csv
import sqlite3
import random
from datetime import datetime, timedelta

def build_turn_1():
    os.makedirs("attendance_logs", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)
    
    # 1. 员工名单：包含干扰项和资质陷阱
    roster = [
        {"id": "CG-001", "name": "Nguyen Tran", "cert": "CNA", "expiry": "2024-12-31", "premium_flag": True},
        {"id": "CG-002", "name": "Elena Smith", "cert": "HHA", "expiry": "2023-11-15", "premium_flag": False}, # 资质过期陷阱
        {"id": "CG-003", "name": "Marcus Wong", "cert": "LPN", "expiry": "2025-06-01", "premium_flag": False},
        {"id": "CG-004", "name": "Sarah Doe", "cert": "CNA", "expiry": "2024-08-20", "premium_flag": True},
    ]
    with open("caregiver_roster.json", "w") as f:
        json.dump(roster, f, indent=4)

    # 2. 工时记录：故意制造违规数据
    # CG-003 在没有 premium_flag 的情况下单周超过 40 小时
    # CG-005 是幽灵员工
    logs = [
        ["date", "caregiver_id", "hours", "task_type"],
        ["2023-10-01", "CG-001", 10, "Personal Care"],
        ["2023-10-01", "CG-003", 13, "Housekeeping"], # 单日超12小时违规
        ["2023-10-02", "CG-003", 10, "Personal Care"],
        ["2023-10-03", "CG-003", 10, "Personal Care"],
        ["2023-10-04", "CG-003", 10, "Personal Care"],
        ["2023-10-05", "CG-005", 8, "Meal Prep"],    # 幽灵员工
        ["2023-10-06", "CG-003", 10, "Personal Care"], # CG-003 周总工时 53，无 premium_flag，严重违规
    ]
    with open("attendance_logs/october_raw.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(logs)

def build_turn_2():
    # 1. 紧急请求数据
    requests = [
        ["request_id", "location", "required_cert", "estimated_days"],
        ["REQ-OR-01", "Orange County", "CNA", 10],
        ["REQ-OR-02", "Orange County", "LPN", 5]
    ]
    with open("urgent_requests.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(requests)

    # 2. 患者分配数据库 (SQLite)：增加复杂性
    conn = sqlite3.connect("patient_assignments.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE assignments (caregiver_id TEXT, patient_name TEXT, risk_level TEXT)")
    # CG-001 负责高风险病人，不能被抽调，虽然他是唯一符合条件的 CNA 且有 premium_flag
    cursor.execute("INSERT INTO assignments VALUES ('CG-001', 'Mrs. Gable', 'High-Risk')")
    cursor.execute("INSERT INTO assignments VALUES ('CG-004', 'Mr. Henderson', 'Low-Risk')")
    conn.commit()
    conn.close()

def build_turn_3():
    # 1. 举报信：引入新的冲突
    reports = [
        {
            "reporter": "Anonymous",
            "subject": "CG-004",
            "incident": "Reported 8 hours on 2023-10-10 but was seen at a local mall.",
            "severity": "High"
        }
    ]
    with open("incident_reports.json", "w") as f:
        json.dump(reports, f, indent=4)

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
