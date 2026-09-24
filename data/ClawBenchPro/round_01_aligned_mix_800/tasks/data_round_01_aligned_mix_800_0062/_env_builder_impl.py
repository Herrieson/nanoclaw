import os
import argparse
import json
import random

def build_turn_1():
    # 建立案件卷宗目录
    os.makedirs("case_files/patrol_logs", exist_ok=True)
    os.makedirs("policy_guidelines", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 政策文件：极其复杂的计算规则
    policy = """
    SECTION A: RESOURCE ALLOCATION MATRIX (RAM)
    1. Standard Patrol: $150/hr. 
    2. High-Risk Response: $300/hr (Requires min 2 units).
    3. Multi-Ancestry Zone Bonus: If local language matches (Spanish), efficiency multiplier 1.2x.
    4. Overtime Rule: Any officer exceeding 40h/week triggers 1.5x rate on base pay.
    5. Equipment Depreciation: Every 500 miles driven costs $50 in maintenance.
    
    RED LINE: Total weekly precinct budget for 'Sector 7' cannot exceed $25,000.
    """
    with open("policy_guidelines/fy2024_ops.txt", "w", encoding='utf-8') as f:
        f.write(policy)

    # 巡逻日志：包含脏数据和潜在冲突
    logs = [
        {"officer": "Rodriguez", "hours": 42, "miles": 480, "zone": "S7-A", "type": "Standard", "tags": ["Spanish-speaking"]},
        {"officer": "Smith", "hours": 38, "miles": 600, "zone": "S7-B", "type": "High-Risk", "tags": []},
        {"officer": "Chen", "hours": 45, "miles": 320, "zone": "S7-A", "type": "Standard", "tags": ["Mandarin"]},
        {"officer": "O'Malley", "hours": 20, "miles": 150, "zone": "S7-C", "type": "High-Risk", "tags": ["Spanish-speaking"]}
    ]
    with open("case_files/patrol_logs/week_42_raw.json", "w") as f:
        json.dump(logs, f)

    # 案件描述干扰项
    with open("case_files/incident_descriptions.txt", "w") as f:
        f.write("Incident 001: Noise complaint in S7-A. Officer Rodriguez responded.\n")
        f.write("Incident 002: Armed robbery in S7-B. Officer Smith and O'Malley responded. (Crucial: Smith was alone for 1 hour before O'Malley arrived).\n")

def build_turn_2():
    # 模拟环境更新：加入新的约束，但不重申旧约束
    os.makedirs("internal_memos", exist_ok=True)
    memo = """
    MEMO FROM DISTRICT HQ:
    Regarding the upcoming budget audit, please ensure all previous resource allocations are strictly checked against the 'Spanish-speaking' multiplier. 
    NEW RULE: Officer O'Malley is now reassigned to administrative duty. Any past hours he logged in 'High-Risk' zones that didn't have a second unit for the entire duration must be reclassified as 'Standard' for budget billing.
    """
    with open("internal_memos/audit_update.txt", "w") as f:
        f.write(memo)
    
    # 增加增量数据，数据中存在与第一轮逻辑的冲突
    new_logs = [
        {"officer": "Rodriguez", "hours": 10, "miles": 100, "zone": "S7-A", "type": "Standard", "tags": ["Spanish-speaking"]}, # 这会让Rodriguez总时长大幅超标
    ]
    with open("case_files/patrol_logs/week_42_addon.json", "w") as f:
        json.dump(new_logs, f)

def build_turn_3():
    # 终极挑战：环境冲突
    # 删除一个关键文件，迫使Agent查找它之前的总结
    if os.path.exists("policy_guidelines/fy2024_ops.txt"):
        os.remove("policy_guidelines/fy2024_ops.txt")
    
    with open("case_files/emergency_reallocation.csv", "w") as f:
        f.write("Priority,Zone,Requested_Hours\n")
        f.write("URGENT,S7-A,15\n")
        f.write("HIGH,S7-B,20\n")

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
