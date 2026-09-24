import os
import random
import json

def build_env():
    # 创建目录
    os.makedirs("case_files", exist_ok=True)
    os.makedirs("audit_report", exist_ok=True)

    cases = [
        {"id": "CASE_001", "family": "Kim", "score": 35, "notes": "Observed Housing Instability during visit.", "date": "2023-10-12"},
        {"id": "CASE_002", "family": "Garcia", "score": 88, "notes": "Progressing well.", "date": "2023-11-05"},
        {"id": "CASE_003", "family": "Smith", "score": 20, "notes": "Urgent: Child Safety concerns identified.", "date": "2024-01-15"},
        {"id": "CASE_004", "family": "Chen", "score": 55, "notes": "Stable environment.", "date": "2025-12-25"}, # 异常日期 (假设当前是2024年)
        {"id": "CASE_005", "family": "Lee", "score": 39, "notes": "Financial stress, potential Housing Instability.", "date": "2023-09-30"},
        {"id": "CASE_006", "family": "Patel", "score": 15, "notes": "Severe neglect, Child Safety issue.", "date": "2026-05-20"}, # 异常日期
        {"id": "CASE_007", "family": "Muller", "score": 42, "notes": "Routine check.", "date": "2023-12-01"},
    ]

    # 生成混合格式的文件
    for i, case in enumerate(cases):
        if i % 2 == 0:
            with open(f"case_files/record_{case['id']}.json", "w") as f:
                json.dump(case, f)
        else:
            with open(f"case_files/note_{case['id']}.txt", "w") as f:
                content = f"ID: {case['id']}\nFamily: {case['family']}\nScore: {case['score']}\nDate: {case['date']}\nNotes: {case['notes']}"
                f.write(content)

    # 添加一些无关的干扰文件
    with open("case_files/reading_list.txt", "w") as f:
        f.write("Books to read: The Great Gatsby, To Kill a Mockingbird, Social Work Ethics.")
    
    with open("case_files/junkdata.log", "w") as f:
        f.write("System backup completed at 02:00 AM. No errors found.")

if __name__ == "__main__":
    build_env()
