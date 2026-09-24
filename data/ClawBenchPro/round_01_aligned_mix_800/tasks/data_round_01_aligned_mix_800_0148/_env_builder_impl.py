import os
import argparse
import json
import random

def build_turn_1():
    # 创建初始审计环境
    os.makedirs("grants/active_projects", exist_ok=True)
    os.makedirs("compliance", exist_ok=True)
    
    # 模拟项目数据：包含金额、行业、合规性瑕疵、地理位置
    projects = [
        {"id": "GP-2024-001", "name": "Urban Greenery Initiative", "allocated": 55000, "sector": "Environment", "region": "South", "last_report_status": "Pending"},
        {"id": "GP-2024-002", "name": "Tech for Elders", "allocated": 82000, "sector": "Education", "region": "North", "last_report_status": "Flagged"},
        {"id": "GP-2024-003", "name": "Rural Health Mobile Unit", "allocated": 120000, "sector": "Healthcare", "region": "West", "last_report_status": "Approved"},
        {"id": "GP-2024-004", "name": "Advocacy for Youth Arts", "allocated": 45000, "sector": "Arts", "region": "South", "last_report_status": "Flagged"},
        {"id": "GP-2024-005", "name": "Clean Water Expansion", "allocated": 95000, "sector": "Environment", "region": "East", "last_report_status": "Approved"}
    ]
    
    for p in projects:
        with open(f"grants/active_projects/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

    # 复杂的合规红线文件（包含一些逻辑陷阱，比如Flagged项目不一定非得撤资，但需要具体原因）
    with open("compliance/policy_v1.txt", "w") as f:
        f.write("Board Policy 2024-A:\n")
        f.write("1. Any project with 'Flagged' status must have its next disbursement suspended until a risk score is calculated.\n")
        f.write("2. Environment projects in the South region are subject to a double-audit due to local regulatory shifts.\n")
        f.write("3. Total overhead across all listed projects must not exceed 15% (details in individual project records).\n")

    # 干扰数据：杂乱的财务日志
    with open("grants/internal_memo.log", "w") as f:
        f.write("2024-03-10: GP-2024-002 reported missing receipts for equipment.\n")
        f.write("2024-03-12: GP-2024-004 failed to submit the diversity impact statement.\n")
        f.write("2024-03-15: Discussion about shifting funds from Arts to Healthcare.\n")

def build_turn_2():
    # 注入新的突发财务文件
    os.makedirs("updates", exist_ok=True)
    new_disbursements = [
        {"id": "GP-2024-003", "request_amount": 30000, "priority": "High"},
        {"id": "GP-2024-005", "request_amount": 15000, "priority": "Medium"}
    ]
    with open("updates/q2_funding_requests.json", "w") as f:
        json.dump(new_disbursements, f, indent=4)
    
    # 修改外部政策限制（产生冲突）
    with open("updates/emergency_notice.txt", "w") as f:
        f.write("EMERGENCY: Due to 501(c)(3) tax-exempt status audit, no single region can exceed 35% of the total current budget allocation. Rebalance immediately.")

def build_turn_3():
    # 第三轮：数据纠偏与最终清算
    # 增加一个隐藏的文件，显示之前某个“Approved”的项目其实也存在合规风险
    with open("compliance/whistleblower_report.json", "w") as f:
        json.dump({
            "target": "GP-2024-005",
            "issue": "Unreported lobbyist activities",
            "timestamp": "2024-04-01"
        }, f, indent=4)

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
