import os
import sqlite3
import json

def build_env():
    base_path = "assets/data_118"
    os.makedirs(base_path, exist_ok=True)

    # 1. 模拟混乱的文件系统
    # 错误的版本和正确的版本
    assessment_data_v1 = {"Emma": [60, 70], "Liam": [55, 65]} # 旧的
    assessment_data_final = {
        "Emma": {"scores": [82, 75, 88], "missed_ids": [101, 105, 110, 112, 115]},
        "Liam": {"scores": [60, 72, 68], "missed_ids": [102, 103, 108, 115, 120]}
    }

    with open(os.path.join(base_path, "grades_draft_v1.json"), "w") as f:
        json.dump(assessment_data_v1, f)
    
    # 故意混淆文件名
    with open(os.path.join(base_path, "notes_from_last_week_FINAL_USE_THIS.json"), "w") as f:
        json.dump(assessment_data_final, f)

    # 2. 题库片段
    q_bank = {
        101: "Who wrote the Declaration of Independence?",
        102: "What is the supreme law of the land?",
        103: "How many amendments does the Constitution have?",
        105: "What are the two parts of the U.S. Congress?",
        108: "Who is the Commander in Chief of the military?",
        110: "What stops one branch of government from becoming too powerful?",
        112: "We elect a U.S. Senator for how many years?",
        115: "What is the capital of the United States?",
        120: "Who signs bills to become laws?"
    }
    
    for i, (qid, text) in enumerate(q_bank.items()):
        suffix = "a" if i % 2 == 0 else "b"
        with open(os.path.join(base_path, f"q_snippet_{suffix}_{qid}.txt"), "w") as f:
            f.write(f"ID: {qid}\nQuestion: {text}")

    # 3. 损坏的 Python 脚本 (ZeroDivisionError 陷阱)
    script_content = """
def calculate_progress(scores):
    # Bug: if scores is empty, this crashes. Also needs to handle average.
    total = sum(scores)
    count = len(scores)
    return total / count

if __name__ == "__main__":
    import json
    # Placeholder for logic
    print("Tool loaded. Ready to process.")
"""
    with open(os.path.join(base_path, "grade_tool.py"), "w") as f:
        f.write(script_content)

    # 4. Mock 数据库
    db_path = os.path.join(base_path, "student_records.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE records (name TEXT, confidence_score REAL)")
    cursor.execute("INSERT INTO records VALUES ('Emma', 0.0)")
    cursor.execute("INSERT INTO records VALUES ('Liam', 0.0)")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
