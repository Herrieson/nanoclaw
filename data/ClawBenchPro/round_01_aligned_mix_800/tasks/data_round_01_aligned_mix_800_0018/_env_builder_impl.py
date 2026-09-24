import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟医院科室的初始混乱状态
    os.makedirs("staffing", exist_ok=True)
    os.makedirs("department_rules", exist_ok=True)
    os.makedirs("schedules", exist_ok=True)

    # 1. 员工基本信息与资质（包含多重依赖）
    staff_data = [
        ["id", "name", "role", "certifications", "hourly_rate", "years_exp"],
        ["RN001", "Maria Garcia", "Registered Nurse", "ICU, ACLS", "55", "15"],
        ["RN002", "James Wilson", "Registered Nurse", "ACLS", "48", "8"],
        ["RN003", "Linda Chen", "Registered Nurse", "PALS, ACLS", "52", "12"],
        ["LPN01", "Robert Miller", "Licensed Practical Nurse", "Basic", "35", "5"],
        ["RN004", "Sarah Thompson", "Registered Nurse", "ICU", "50", "3"],
        ["RN005", "David Rodriguez", "Registered Nurse", "ACLS", "49", "6"]
    ]
    with open("staffing/nurses.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(staff_data)

    # 2. 复杂的排班限制（文本格式，增加理解难度）
    rules = """
    Department Policy 2024-Q3:
    - Each shift MUST have at least one RN with ICU certification.
    - Total labor cost for this weekend (Sat-Sun) cannot exceed $8,500.
    - No nurse can work more than 12 consecutive hours.
    - Overtime (over 40h/week) is paid at 1.5x, but we try to avoid it.
    - Current Week Cumulative Hours (pre-weekend):
      RN001: 36h, RN002: 40h, RN003: 32h, LPN01: 40h, RN004: 20h, RN005: 38h.
    """
    with open("department_rules/policy_v1.txt", "w") as f:
        f.write(rules)

    # 3. 初始排班申请（存在冲突）
    requests = {
        "Saturday_Day": ["RN002", "RN004", "LPN01"],
        "Saturday_Night": ["RN001", "RN003"],
        "Sunday_Day": ["RN002", "RN005", "LPN01"],
        "Sunday_Night": ["RN001", "RN004"]
    }
    with open("schedules/requests.json", "w", encoding="utf-8") as f:
        json.dump(requests, f)

def build_turn_2():
    # 模拟紧急情况：新规下达和人员变动
    os.makedirs("notices", exist_ok=True)
    
    # 注入新的约束，但不重复第一轮的预算和证书要求
    with open("notices/urgent_update.txt", "w") as f:
        f.write("Update: Due to the flu season surge, all Night shifts MUST now have at least two Registered Nurses. "
                "Also, RN001 just called in - she has a family emergency and cannot work Sunday Night. "
                "Find a replacement that still respects our budget and the rules we established earlier.")

def build_turn_3():
    # 模拟最终审计和逻辑冲突
    os.makedirs("audit", exist_ok=True)
    # 增加一份相互矛盾的供应商报告
    external_report = [
        ["provider", "available_nurses", "flat_rate"],
        ["Agency_A", "RN_Temp_01", "85"],
        ["Agency_A", "RN_Temp_02", "85"]
    ]
    with open("audit/external_agency.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(external_report)

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
