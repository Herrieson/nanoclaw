import os
import argparse
import json
import random

def build_turn_1():
    # 创建初始卷宗目录
    os.makedirs("pending_cases", exist_ok=True)
    os.makedirs("firm_database", exist_ok=True)
    
    # 历史客户数据库（干扰项与冲突来源）
    # 包含一些看起来不相关但在法律上构成冲突的关系
    firm_clients = [
        {"id": "C001", "name": "Global Pharma Corp", "related_entities": ["GP Research", "BioSafe Inc"], "status": "Active"},
        {"id": "C002", "name": "Marcus Vane", "role": "Former CEO of TechLink", "status": "Inactive"},
        {"id": "C003", "name": "City of Phoenix", "status": "Permanent Client"}
    ]
    with open("firm_database/clients.json", "w") as f:
        json.dump(firm_clients, f, indent=4)

    # 待审理的新委托案件
    # 案件A：直接涉及 BioSafe (属于 C001 的子公司，存在直接利益冲突)
    case_a = {
        "case_id": "L-2024-001",
        "client": "GreenEco NGO",
        "opponent": "BioSafe Inc",
        "matter": "Environmental violation lawsuit",
        "estimated_hours": 120
    }
    # 案件B：涉及 Marcus Vane 的现任秘书（间接冲突，需Agent判断）
    case_b = {
        "case_id": "L-2024-002",
        "client": "Elena Rossi",
        "opponent": "TechLink Board",
        "matter": "Wrongful termination",
        "estimated_hours": 85
    }
    # 案件C：看似正常
    case_c = {
        "case_id": "L-2024-003",
        "client": "James Holden",
        "opponent": "Mars Freight Services",
        "matter": "Contract dispute",
        "estimated_hours": 200
    }

    with open("pending_cases/new_intake.json", "w") as f:
        json.dump([case_a, case_b, case_c], f, indent=4)

    # 包含一些杂乱的邮件原始记录，需要解析出“红线”
    policy_notes = """
    From: Senior Partner
    Subject: Conflict Policy REMINDER
    1. We NEVER take cases against current active clients or their listed subsidiaries.
    2. Any former CEO-related litigation must be flagged if it happened within 2 years.
    3. We need a summary of accepted cases in 'case_load_report' with total projected hours. 
    4. Keep your own notes on why you rejected something, I don't want to explain this to the committee twice.
    """
    with open("internal_memo.txt", "w") as f:
        f.write(policy_notes)

def build_turn_2():
    # 注入新文件，模拟第二天的突发情况
    os.makedirs("updates", exist_ok=True)
    
    # 证据链发现：James Holden 的对手公司其实是 City of Phoenix 的影子合伙人
    # 这会推翻 Turn 1 接受 Case C 的决定
    new_intel = {
        "discovery_id": "D-992",
        "target": "Mars Freight Services",
        "found_links": ["City of Phoenix Urban Development Fund (60% ownership)"],
        "note": "This connection was hidden behind a shell company."
    }
    with open("updates/confidential_discovery.json", "w") as f:
        json.dump(new_intel, f, indent=4)

def build_turn_3():
    # 第三轮：资源超载
    # 增加一个紧急案件，但时间已经不够了
    os.makedirs("urgent", exist_ok=True)
    with open("urgent/emergency.txt", "w") as f:
        f.write("URGENT: New client 'State Pension' wants to sue 'Global Pharma Corp'. This is huge money but massive conflict. Also, we found out Elena Rossi's case (L-2024-002) is actually time-barred. Check your records on the 2-year rule mentioned in the first memo and our current workload.")

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
