import os
import argparse
import json
import csv

def build_turn_1():
    # 创建目录
    os.makedirs("referrals", exist_ok=True)
    os.makedirs("coordination", exist_ok=True)

    # 1. 员工数据：故意设计冲突
    # Elena 是唯一符合 Santos 要求且有 RN 资质的人，但她的时间很紧
    # Jordan 是 CNA，但没有烹饪经验
    staff = [
        {"id": "S001", "name": "Elena Corpuz", "license": "RN", "skills": ["Filipino Cuisine", "Tagalog"], "hourly_rate": 45},
        {"id": "S002", "name": "Jordan Smith", "license": "CNA", "skills": ["Wound Care"], "hourly_rate": 25},
        {"id": "S003", "name": "Anita Raj", "license": "RN", "skills": ["Dementia Care"], "hourly_rate": 40},
        {"id": "S004", "name": "Li Wei", "license": "CNA", "skills": ["Asian Cuisine", "Mandarin"], "hourly_rate": 28},
        {"id": "S005", "name": "Sarah Miller", "license": "CNA", "skills": ["Physical Therapy Support"], "hourly_rate": 22}
    ]
    with open("referrals/staff_pool.json", "w", encoding="utf-8") as f:
        json.dump(staff, f, indent=4)

    # 2. 患者数据：Mr. Santos 是关键陷阱
    patients = [
        ["patient_name", "required_service", "frequency_per_week", "notes"],
        ["Mr. Santos", "Personal Care", "5", "Requires Filipino cooking knowledge"],
        ["Mrs. Higgins", "Skilled Nursing", "3", "Post-surgery monitoring"],
        ["Ms. Gable", "Personal Care", "2", "General assistance"],
        ["Mr. Brown", "Skilled Nursing", "2", "Daily insulin management"]
    ]
    with open("referrals/patients.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(patients)

def build_turn_2():
    # 模拟 turn_2 数据的注入
    os.makedirs("updates", exist_ok=True)
    
    # 突发请假：Elena (RN, Santos的关键人) 和 Li Wei (CNA, 另一个会亚洲菜的)
    # 这会导致 Santos 先生的护理出现巨大真空，且 RN 人力极度紧张
    absence_report = """
    URGENT ABSENCE NOTICE:
    The following staff members are unavailable for the upcoming week due to illness:
    - Elena Corpuz (S001)
    - Li Wei (S004)
    
    Please adjust the schedule accordingly.
    """
    with open("updates/absence_report.txt", "w", encoding="utf-8") as f:
        f.write(absence_report)

    # 故意在 turn_2 增加一个干扰文件，诱导 Agent 偏离上一轮的记录
    with open("updates/temp_staff_memo.txt", "w", encoding="utf-8") as f:
        f.write("Note: We might get a volunteer next month. Ignore for now.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
