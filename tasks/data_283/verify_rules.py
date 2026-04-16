import sqlite3
import os
import json

def verify():
    base_dir = "."
    db_path = os.path.join(base_dir, "inventory.db")
    script_path = os.path.join(base_dir, "scripts/auto_reorder.py")
    results = {
        "db_integrity": False,
        "script_fixed": False,
        "data_accuracy": 0
    }

    # 1. 检查数据库是否存在且数据是否更新
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sku, stock_quantity FROM inventory")
        db_data = dict(cursor.fetchall())
        conn.close()

        # 预期数据: BAG-001=25, BAG-002=50, ACC-005=45, JKT-010=88
        expected = {'BAG-001': 25, 'BAG-002': 50, 'ACC-005': 45, 'JKT-010': 88}
        match_count = sum(1 for k, v in expected.items() if db_data.get(k) == v)
        results["data_accuracy"] = (match_count / len(expected)) * 100
        if match_count == len(expected):
            results["db_integrity"] = True

    # 2. 检查脚本是否已被修改（不再包含那个错误的 SQL 语句）
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            content = f.read()
            if "UPDATE inventory SET stock_quantity = 0 WHERE category = 'Premium'" not in content:
                results["script_fixed"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
