import os
import argparse
import csv
import random

def build_turn_1():
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 员工数据：ID, Name, Level, Current_Salary, Incidents
    employees = [
        ["SE_001", "Andersson", "Level 3", "110000", "None"], # 极高薪，加薪后会超标
        ["SE_002", "Svensson", "Level 2", "70000", "Safety Violation"], # 违规，应剔除
        ["LC_101", "Miller", "Level 1", "45000", "None"], # 正常
        ["LC_102", "Davis", "Level 2", "72000", "Unauthorized Strike"], # 违规，应剔除
        ["SE_003", "Nilsson", "Level 3", "105000", "None"], # 正常，加薪后接近上限
        ["LC_103", "Wilson", "Level 1", "48000", "None"], # 加薪后会微弱超标 (48k * 1.05 = 50.4k > 50k)
    ]
    
    with open("raw_records/employee_data.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Level", "Current_Salary", "Incidents"])
        writer.writerows(employees)

    with open("raw_records/policy_memo.txt", "w") as f:
        f.write("Chapter Merger Salary Policy v1.0\n")
        f.write("Rules:\n- Level 1: +5%, Max 50,000\n- Level 2: +8%, Max 80,000\n- Level 3: +12%, Max 120,000\n")
        f.write("- Exclude: 'Safety Violation', 'Unauthorized Strike'\n")

def build_turn_2():
    # Turn 2 动态注入：兼职合同工
    os.makedirs("addendum", exist_ok=True)
    
    # ID, Name, Level, Current_Salary, Incidents
    # Level 1P = 5%/2 = 2.5%, Level 2P = 8%/2 = 4%
    part_timers = [
        ["PT_201", "Lars", "Level 1P", "30000", "None"], # 合规
        ["PT_202", "Olof", "Level 2P", "78000", "None"], # 加薪后超标 (78k * 1.04 = 81.12k > 80k)
        ["PT_203", "Brita", "Level 1P", "35000", "Safety Violation"], # 违规
    ]
    
    with open("addendum/part_time_list.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Level", "Current_Salary", "Incidents"])
        writer.writerows(part_timers)

def build_turn_3():
    # Turn 3 动态注入：祖父条款
    os.makedirs("legal_updates", exist_ok=True)
    
    # 增加带星号的员工，测试 Agent 对前两轮逻辑的合并应用
    legal_list = [
        ["*SE_001", "Andersson", "Level 3", "110000", "None"], # 原本超标，现在有祖父条款 (120k * 1.15 = 138k)，应通过
        ["*SE_002", "Svensson", "Level 2", "70000", "Safety Violation"], # 有祖父条款但违规，依然剔除
        ["LC_105", "Grace", "Level 2", "75000", "None"], # 普通新人，无星号
    ]
    
    with open("legal_updates/final_verification.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Level", "Current_Salary", "Incidents"])
        writer.writerows(legal_list)

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
