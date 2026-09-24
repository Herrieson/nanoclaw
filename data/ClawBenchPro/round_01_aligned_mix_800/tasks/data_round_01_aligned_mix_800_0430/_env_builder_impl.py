import os
import json
import csv
import random

def build_env():
    random.seed(42)
    
    # 核心目录建立
    dirs_to_make = [
        "administration/rosters",
        "teacher_notes",
        "assessments",
        "conference_materials"
    ]
    for d in dirs_to_make:
        os.makedirs(d, exist_ok=True)
        
    # --- 1. 生成大批量 Roster (信息伪装与噪音) ---
    def generate_students(start_id, count, prefix="STU-"):
        return [{"id": f"{prefix}{str(i).zfill(4)}", "name": f"Student_Name_{i}"} for i in range(start_id, start_id + count)]

    rosters = {
        "2021_2022_all.csv": (generate_students(1000, 150), "archived"),
        "2022_2023_all.csv": (generate_students(1100, 160), "archived"),
        "2023_2024_withdrawn.csv": (generate_students(1200, 30), "withdrawn"),
        "2023_2024_active.csv": (generate_students(1300, 200), "active")
    }
    
    active_ids = []
    withdrawn_ids = []
    
    for filename, (students, status) in rosters.items():
        filepath = os.path.join("administration", "rosters", filename)
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "full_name", "status"])
            for s in students:
                writer.writerow([s["id"], s["name"], status])
                if status == "active" and filename == "2023_2024_active.csv":
                    active_ids.append(s["id"])
                if status == "withdrawn":
                    withdrawn_ids.append(s["id"])

    # 随机生成幽灵ID
    ghost_ids = [f"STU-99{str(i).zfill(2)}" for i in range(20)]
    
    # --- 2. 生成 Teacher Notes (线索隐藏与规则发现) ---
    # 生成几十个废话文件
    for i in range(50):
        with open(f"teacher_notes/note_{i}.txt", "w", encoding="utf-8") as f:
            f.write(f"Random thoughts on day {i}... The garden needs watering. System still broken.\n")
            if i % 3 == 0:
                f.write("Old grading was A=90, B=80... but I changed it. Don't use this!\n")
    
    # 真正的规则文件
    real_rubric = """
This is my OFFICIAL 2023-2024 GRADING RUBRIC:
Because the district changed the policy, the conversions are:
A: 95
B: 85
C: 75
D: 65
F: 40

Alert! If a student's average is strictly less than 68.0, they must be flagged as 'Needs Attention'. Otherwise they are 'OK'.
"""
    with open("teacher_notes/meeting_memo_v2_final.txt", "w", encoding="utf-8") as f:
        f.write(real_rubric)

    # --- 3. 生成海量 assessments (信息极度碎片化与噪音) ---
    weeks = [f"week_{str(i).zfill(2)}" for i in range(1, 11)]
    subjects = ["math", "science", "history", "art"]
    
    # 模拟分数生成器
    def get_random_score():
        if random.random() > 0.3:
            return random.choice([95, 85, 75, 65, 40, 100, 92, 88, 76, 60, 55])
        else:
            return random.choice(["A", "B", "C", "D", "F"])

    def create_assessment_file(folder, file_idx, student_list):
        os.makedirs(folder, exist_ok=True)
        file_type = random.choice(["json", "csv", "log"])
        
        # 挑选一部分学生生成成绩
        sampled_students = random.sample(student_list, min(len(student_list), random.randint(10, 30)))
        
        if file_type == "json":
            data = []
            id_key = random.choice(["id", "student_id", "STU_ID"])
            score_key = random.choice(["score", "grade", "result"])
            for sid in sampled_students:
                data.append({id_key: sid, score_key: get_random_score()})
            with open(os.path.join(folder, f"data_{file_idx}.json"), "w", encoding="utf-8") as f:
                json.dump(data, f)
                
        elif file_type == "csv":
            id_key = random.choice(["id", "student_id", "STU_ID"])
            score_key = random.choice(["score", "grade", "result"])
            with open(os.path.join(folder, f"records_{file_idx}.csv"), "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([id_key, score_key])
                for sid in sampled_students:
                    writer.writerow([sid, get_random_score()])
                    
        elif file_type == "log":
            with open(os.path.join(folder, f"syslog_{file_idx}.log"), "w", encoding="utf-8") as f:
                for sid in sampled_students:
                    f.write(f"Record -> ID: {sid} | Result: {get_random_score()}\n")

    # 遍历生成文件结构
    for w in weeks:
        for subj in subjects:
            base_dir = os.path.join("assessments", w, subj)
            os.makedirs(base_dir, exist_ok=True)
            
            # 正常目录生成 (包含有效学生、退学学生和幽灵ID的混合数据)
            pool = active_ids + withdrawn_ids + ghost_ids
            for i in range(random.randint(2, 5)):
                create_assessment_file(base_dir, i, pool)
            
            # 生成带 _backup 后缀的废弃文件 (Agent必须跳过)
            if random.random() > 0.7:
                backup_dir = os.path.join(base_dir, "old_backup_ignore")
                for i in range(2):
                    create_assessment_file(backup_dir, i, pool)
            
            # 在正常文件夹下直接放名字带 _backup 的文件
            if random.random() > 0.8:
                create_assessment_file(base_dir, "sys_backup", pool)

    # 确保每个 active_id 至少有一个合法文件中的成绩，以免平均分除以0
    # 我们在一个保证不带 ignore/backup 的目录中强行写一个大文件
    guarantee_dir = os.path.join("assessments", "week_01", "math")
    os.makedirs(guarantee_dir, exist_ok=True)
    with open(os.path.join(guarantee_dir, "guarantee.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "score"])
        for sid in active_ids:
            writer.writerow([sid, random.randint(70, 100)])

if __name__ == "__main__":
    build_env()
