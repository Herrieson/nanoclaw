import os
import argparse
import json
import csv

def build_turn_1():
    # 初始环境：规则说明、大量混乱格式的提案
    os.makedirs("raw_submissions", exist_ok=True)
    os.makedirs("evaluation_results", exist_ok=True)
    
    # 核心规则
    rules = """
    COMPETITION RULES v1.0
    1. Grade Groups: K-5 (Elementary), 6-8 (Middle).
    2. Budget Cap: 
       - Elementary: $2000 per project.
       - Middle: $3500 per project.
    3. Tech Requirement: Must include at least one Ed-Tech component (e.g., Tablet-based learning, AI, Robotics, VR).
    4. Interdisciplinary: Must combine at least two subjects (e.g., Math + Art).
    5. Scoring: Score = (Innovation * 0.4) + (Feasibility * 0.3) + (Budget_Efficiency * 0.3).
    """
    with open("competition_rules.txt", "w") as f:
        f.write(rules)

    # 提案数据 - 混合格式
    # 提案 A: 合规 (Middle School)
    p_a = {
        "id": "PRO-2024-001",
        "title": "Robo-Math Challenge",
        "lead_teacher": "Dr. Aris",
        "grade_level": "7",
        "subjects": ["Mathematics", "Engineering"],
        "budget": 3200,
        "tech_stack": "Lego Mindstorms, Python",
        "duration_weeks": 4,
        "start_week": 12
    }
    with open("raw_submissions/proposal_001.json", "w") as f:
        json.dump(p_a, f)

    # 提案 B: 预算超标干扰项
    p_b = """
    # Project: Renaissance Art in VR
    Teacher: Sarah Miller
    Target: 4th Grade
    Subjects: History, Art
    Budget: $2500 (Over cap!)
    Tech: Meta Quest 3
    Timeline: 3 weeks starting from Week 14
    """
    with open("raw_submissions/proposal_002.md", "w") as f:
        f.write(p_b)

    # 提案 C: 缺乏科技元素干扰项
    p_c = "ID: 003, Title: Garden Ecology, Teacher: John Doe, Grade: 6, Subjects: Biology, Budget: 1500, Tech: None (Physical tools only), Week: 10-12"
    with open("raw_submissions/proposal_003.txt", "w") as f:
        f.write(p_c)

    # 提案 D: 合规 (Elementary)
    p_d = {
        "id": "PRO-2024-004",
        "title": "Interactive Storytelling AI",
        "lead_teacher": "Elena's Peer (Ms. Gable)",
        "grade_level": "3",
        "subjects": ["English", "Computer Science"],
        "budget": 1800,
        "tech_stack": "ChatGPT API, Scratch",
        "duration_weeks": 2,
        "start_week": 15
    }
    with open("raw_submissions/proposal_004.json", "w") as f:
        json.dump(p_d, f)

def build_turn_2():
    # 注入突发变更和新提案
    os.makedirs("urgent_updates", exist_ok=True)
    os.makedirs("new_arrivals", exist_ok=True)
    
    # 预算紧缩：所有上限下调 10%
    # 供应商黑名单：所有涉及 "Meta" 或 "Lego" 的硬件由于安全审核未通过，暂不可用
    memo = {
        "update_date": "2024-10-25",
        "budget_cut_ratio": 0.10,
        "blacklisted_suppliers": ["Meta", "Lego"],
        "instruction": "Re-evaluate all existing candidates and new ones."
    }
    with open("urgent_updates/memo.json", "w") as f:
        json.dump(memo, f)
        
    # 新提交的提案 E: 看起来完美但踩了黑名单（Lego）
    p_e = {
        "id": "PRO-2024-005",
        "title": "Future City",
        "lead_teacher": "Mr. Smith",
        "grade_level": "8",
        "subjects": ["Social Studies", "Physics"],
        "budget": 2800,
        "tech_stack": "Lego Architecture, CAD",
        "duration_weeks": 5,
        "start_week": 18
    }
    with open("new_arrivals/proposal_005.json", "w") as f:
        json.dump(p_e, f)

def build_turn_3():
    # 教师课表冲突数据
    # 列出几个老师在特定周次的忙碌情况
    schedule = [
        ["Teacher", "Week_12_Status", "Week_13_Status", "Week_14_Status", "Week_15_Status", "Week_16_Status"],
        ["Dr. Aris", "Teaching", "Teaching", "Teaching", "Field Trip", "Teaching"], # 如果项目在12周开始，持续4周，会冲突
        ["Ms. Gable", "Free", "Free", "Free", "Teaching", "Free"], # 如果项目在15周开始，持续2周，会冲突
        ["Mr. Smith", "Teaching", "Teaching", "Teaching", "Teaching", "Teaching"]
    ]
    with open("teacher_schedules.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(schedule)
    
    os.makedirs("final_delivery", exist_ok=True)

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
