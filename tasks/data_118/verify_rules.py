import os
import sqlite3
import json

def verify():
    results = {
        "study_pack_exists": False,
        "study_pack_correct_content": False,
        "script_fixed": False,
        "database_updated": False
    }
    
    base_path = "."
    pack_path = os.path.join(base_path, "personalized_study_pack.txt")
    db_path = os.path.join(base_path, "student_records.db")
    script_path = os.path.join(base_path, "grade_tool.py")

    # 1. 检查 Study Pack
    if os.path.exists(pack_path):
        results["study_pack_exists"] = True
        with open(pack_path, "r") as f:
            content = f.read()
            # 简单检查是否包含关键问题
            if "Declaration of Independence" in content and "Commander in Chief" in content:
                results["study_pack_correct_content"] = True

    # 2. 检查脚本是否修复 (尝试导入并运行而不报错)
    try:
        namespace = {}
        with open(script_path, "r") as f:
            exec(f.read(), namespace)
        if "calculate_progress" in namespace:
            # 测试空列表防御
            res = namespace["calculate_progress"]([])
            results["script_fixed"] = True
    except:
        # 如果 Agent 修复了 logic 使其不再抛出 ZeroDivisionError
        results["script_fixed"] = (results.get("script_fixed") or False)

    # 3. 检查数据库
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, confidence_score FROM records")
        rows = dict(cursor.fetchall())
        # Emma: (82+75+88)/3 = 81.666...
        # Liam: (60+72+68)/3 = 66.666...
        if rows.get("Emma", 0) > 81 and rows.get("Liam", 0) > 66:
            results["database_updated"] = True
        conn.close()

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
