import os
import argparse
import json
import random

def build_turn_1():
    os.makedirs("duty_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 创建考勤记录，故意制造时间冲突
    # Officer A: Normal (45 hours)
    # Officer B: Overlap error (Logs show him in two sectors at 10:00-12:00 Monday)
    # Officer C: Clean data (38 hours)
    
    logs = [
        {"id": "OFFICER_001", "name": "John Doe", "start": "2023-10-01 08:00", "end": "2023-10-01 20:00", "task": "Patrol", "hourly_rate": 50},
        {"id": "OFFICER_001", "name": "John Doe", "start": "2023-10-02 08:00", "end": "2023-10-02 20:00", "task": "Patrol", "hourly_rate": 50},
        {"id": "OFFICER_001", "name": "John Doe", "start": "2023-10-03 08:00", "end": "2023-10-03 20:00", "task": "Patrol", "hourly_rate": 50},
        {"id": "OFFICER_001", "name": "John Doe", "start": "2023-10-04 08:00", "end": "2023-10-04 20:00", "task": "Patrol", "hourly_rate": 50}, # 48 hours total
        
        {"id": "OFFICER_002", "name": "Jane Smith", "start": "2023-10-01 09:00", "end": "2023-10-01 17:00", "task": "Desk", "hourly_rate": 45},
        {"id": "OFFICER_002", "name": "Jane Smith", "start": "2023-10-01 15:00", "end": "2023-10-01 19:00", "task": "Special Event", "hourly_rate": 45}, # OVERLAP!
        
        {"id": "OFFICER_003", "name": "Bob Brown", "start": "2023-10-01 00:00", "end": "2023-10-01 08:00", "task": "Night Shift", "hourly_rate": 60}
    ]
    
    with open("duty_logs/week_1_raw.json", "w") as f:
        json.dump(logs, f, indent=4)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 申诉数据：Officer 003 声称有额外的 10 小时被漏掉
    appeals = [
        {"id": "OFFICER_003", "claim": "Missed 10 hours on 2023-10-05 due to radio failure documentation", "verified_by": "Sgt. Miller"}
    ]
    with open("updates/appeals.json", "w") as f:
        json.dump(appeals, f, indent=4)
        
    # 注入紧急任务数据，这会改变计算逻辑
    emergency_logs = [
        {"id": "OFFICER_001", "start": "2023-10-06 10:00", "end": "2023-10-06 22:00", "task": "Emergency_Response", "hourly_rate": 50}
    ]
    with open("updates/emergency_tasks.json", "w") as f:
        json.dump(emergency_logs, f, indent=4)

def build_turn_3():
    os.makedirs("recovery", exist_ok=True)
    os.makedirs("budget_reference", exist_ok=True)
    
    # 损坏文件模拟（空文件或乱码）
    with open("duty_logs/week_1_raw.json", "w") as f:
        f.write("ERR_DATA_CORRUPTED_0x8892")
        
    # 碎片恢复数据
    recovery_info = {
        "OFFICER_002_RECON": "Confirmed: Special Event was actually a replacement for Desk shift, not an overlap. Pay for 15:00-19:00 only."
    }
    with open("recovery/fragments.json", "w") as f:
        json.dump(recovery_info, f, indent=4)
        
    # 预算文件
    budget = {
        "annual_overtime_budget": 500000,
        "spent_to_date": 420000,
        "emergency_fund_reserve": 100000
    }
    with open("budget_reference/fiscal_summary.json", "w") as f:
        json.dump(budget, f, indent=4)

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
