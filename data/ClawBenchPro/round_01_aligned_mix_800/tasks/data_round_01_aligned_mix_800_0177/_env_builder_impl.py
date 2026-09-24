import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟联邦司法部门的项目申请环境
    os.makedirs("applications/pending", exist_ok=True)
    os.makedirs("guidelines", exist_ok=True)
    
    # 政策文件：包含复杂的打分逻辑
    with open("guidelines/fy24_funding_protocol.txt", "w", encoding="utf-8") as f:
        f.write("FY24 Federal Justice Assistance Grant (FJAG) Protocol\n")
        f.write("1. Eligibility: Minimum 3 years of operation.\n")
        f.write("2. Scoring Weights: Community Impact (40%), Resource Efficiency (30%), Innovation (30%).\n")
        f.write("3. Hard Redlines: No organizations with previous 'High Risk' audit status.\n")
        f.write("4. Geographic Cap: No single tribal area can receive more than 40% of the total monthly pot ($500,000).\n")
    
    # 申请数据：存在脏数据和相互冲突的信息
    apps = [
        {"id": "APP-001", "org": "Mountain-Watchers", "years": 5, "impact_score": 85, "cost": 180000, "audit": "Low Risk", "location": "Zone-A"},
        {"id": "APP-002", "org": "Urban-Safety-First", "years": 2, "impact_score": 90, "cost": 120000, "audit": "Low Risk", "location": "Zone-B"}, # 踩中年限红线
        {"id": "APP-003", "org": "Tribal-Justice-Alliance", "years": 10, "impact_score": 75, "cost": 220000, "audit": "High Risk", "location": "Zone-A"}, # 踩中审计红线
        {"id": "APP-004", "org": "Unity-Law-Clinic", "years": 4, "impact_score": 88, "cost": 150000, "audit": "Low Risk", "location": "Zone-C"},
        {"id": "APP-005", "org": "First-Nations-Legal", "years": 6, "impact_score": 82, "cost": 160000, "audit": "Low Risk", "location": "Zone-A"} # 与001总和超过Zone-A配额
    ]
    
    for app in apps:
        with open(f"applications/pending/{app['id']}.json", "w") as f:
            json.dump(app, f, indent=4)

def build_turn_2():
    # 增加审计历史文件，迫使 Agent 检查更深层次的数据
    os.makedirs("audit_vault", exist_ok=True)
    audit_history = [
        ["OrgName", "FiscalYear", "Status", "Flags"],
        ["Mountain-Watchers", "2022", "Pass", "None"],
        ["Unity-Law-Clinic", "2023", "Pass", "Minor-Documentation"],
        ["First-Nations-Legal", "2021", "High Risk", "Fund-Misuse"], # 历史污点，第一轮可能没发现，因为json里写的是Low Risk
    ]
    with open("audit_vault/historical_integrity.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(audit_history)

def build_turn_3():
    # 突发政策变更
    os.makedirs("emergency_notices", exist_ok=True)
    with open("emergency_notices/budget_update.md", "w") as f:
        f.write("# Urgent: Budget Realignment\n")
        f.write("Due to fiscal adjustments, the total monthly pot is reduced to $350,000 effective immediately.\n")
        f.write("Also, 'First-Nations-Legal' has just been cleared of all historical flags by the court, override any previous risk status.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1: build_turn_1()
    elif args.turn == 2: build_turn_2()
    elif args.turn == 3: build_turn_3()
