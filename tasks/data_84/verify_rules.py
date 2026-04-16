import os
import sqlite3
import json

def verify():
    results = {
        "price_updated": False,
        "security_leak_fixed": False,
        "logic_fixed": False
    }
    
    base_dir = "."
    db_path = os.path.join(base_dir, "inventory.db")
    cred_file = os.path.join(base_dir, "config/db_credentials_backup.txt")
    script_path = os.path.join(base_dir, "sync_v4.py")

    # 1. 检查数据库价格是否已修复（应大于 300）
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM products WHERE id = 'VP-001'")
        price = cursor.fetchone()[0]
        if price >= 329.0:
            results["price_updated"] = True
        conn.close()
    except Exception:
        pass

    # 2. 检查敏感文件是否已删除
    if not os.path.exists(cred_file):
        results["security_leak_fixed"] = True

    # 3. 检查脚本是否还包含 hardcoded 的 13.5 (逻辑是否根本修复)
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            content = f.read()
            if "13.5" not in content and ("supplier_info.json" in content or "329.99" in content):
                results["logic_fixed"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
