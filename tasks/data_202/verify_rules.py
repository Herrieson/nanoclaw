import os
import sqlite3
import json

def verify():
    results = {
        "db_repaired": False,
        "script_fixed": False,
        "report_generated": False,
        "correct_math": False
    }
    
    base_path = "."
    db_path = os.path.join(base_path, "storage/inventory.db")
    report_path = os.path.join(base_path, "stock_report.txt")
    script_path = os.path.join(base_path, "process_orders.py")

    # 1. 检查脚本是否修复 (不再包含逻辑位移错误)
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            content = f.read()
            if "<<" not in content and "stock_level -" in content:
                results["script_fixed"] = True

    # 2. 检查数据库状态与计算逻辑
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # 检查 Zimmermann Rotors (ID 4) 的库存
            # 初始 8, 逻辑错误减去了 240, 如果修复了应该反映 log 中的变化
            # Log 说又用了 4 个，所以 8 - 4 = 4
            cursor.execute("SELECT stock_level FROM parts WHERE id=4")
            val = cursor.fetchone()[0]
            if val == 4:
                results["correct_math"] = True
            results["db_repaired"] = True
            conn.close()
        except:
            pass

    # 3. 检查报告是否存在
    if os.path.exists(report_path):
        results["report_generated"] = True
        with open(report_path, 'r') as f:
            report_content = f.read().lower()
            if "bosch" in report_content and "zimmermann" in report_content:
                results["report_content_ok"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
