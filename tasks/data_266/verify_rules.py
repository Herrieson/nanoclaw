import os
import sqlite3
import json

def verify():
    base_path = "."
    report_path = "final_report.txt"
    db_path = os.path.join(base_path, "result.db")
    results = {
        "db_exists": False,
        "error_handled": False,
        "multiplier_correct": False,
        "report_generated": False
    }

    # 1. 检查数据库是否按要求生成
    if os.path.exists(db_path):
        results["db_exists"] = True
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # 2. 检查逻辑修复情况：ID 004 的 VAL 是 4500，4500 * 0.85 * 1.2 = 4590
            cursor.execute("SELECT impact_score FROM impact WHERE id='ID:004'")
            row = cursor.fetchone()
            if row and abs(row[0] - 4590) < 0.01:
                results["multiplier_correct"] = True
            
            # 3. 检查是否处理了异常数据（ID:003 不应出现在库中，或者被妥善处理）
            cursor.execute("SELECT COUNT(*) FROM impact WHERE id='ID:003'")
            if cursor.fetchone()[0] == 0:
                results["error_handled"] = True
            conn.close()
        except:
            pass

    # 4. 检查报告是否存在
    if os.path.exists(report_path):
        results["report_generated"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
