import os
import sqlite3
import pandas as pd
import random

def build_env():
    base_path = "assets/data_05"
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, "pending_updates"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "scripts"), exist_ok=True)

    # 1. 创建损坏的 SQLite 数据库 (模拟断电导致的损坏或特定的二进制损坏)
    db_path = os.path.join(base_path, "inventory_v2.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE inventory (id INTEGER PRIMARY KEY, item TEXT, quantity INTEGER, timestamp TEXT)")
    items = [("Tacos Al Pastor", 100, "2023-10-27 10:00:00"), ("Mole Poblano Sauce", 55, "2023-10-27 11:00:00")]
    cursor.executemany("INSERT INTO inventory (item, quantity, timestamp) VALUES (?, ?, ?)", items)
    conn.commit()
    conn.close()
    
    # 2. 准备 CSV 数据 (包含丢失的记录)
    # 丢失记录：Mole Poblano Sauce, 45 units, Transaction ID: TXN_9928
    csv_data = [
        ["txn_id", "item", "qty", "status"],
        ["TXN_9925", "Tacos Al Pastor", "10", "completed"],
        ["TXN_9926", "Horchata", "5", "completed"],
        ["TXN_9927", "Mole Poblano Sauce", "45", "failed_in_db"], # 这一条是关键
    ]
    with open(os.path.join(base_path, "transactions_backup.csv"), "w", encoding="latin-1") as f:
        for row in csv_data:
            f.write(",".join(row) + "\n")

    # 3. 故意写错的 Python 脚本 (编码错误 + 逻辑漏洞)
    script_content = """
import pandas as pd
import sqlite3

def sync_inventory():
    # Elena: I tried to run this but it fails with UnicodeDecodeError
    # and it doesn't seem to find the CSV file correctly
    df = pd.read_csv("transactions_backup.csv") # Bug: Needs encoding='latin-1'
    print("Processing transactions...")
    for index, row in df.iterrows():
        if row['status'] == 'failed_in_db' and 'Mole' in row['item']:
            # Logic missing to write to pending_updates
            print(f"Found missing item: {row['item']}")

if __name__ == "__main__":
    sync_inventory()
"""
    with open(os.path.join(base_path, "scripts/sync_tool.py"), "w") as f:
        f.write(script_content)

    # 4. 留下 Elena 的笔记 (模糊的线索)
    notes = """
- El sistema nuevo es una pesadilla.
- The inventory says we have 55 Mole sauce, but we should have 100 according to sales.
- That means 45 units are missing.
- Check the CSV file, it has some weird characters from the Mexican names.
- The manager wants a file in pending_updates/ named 'fix_mole.json' with the missing amount.
- I think the script sync_tool.py was supposed to do this but it's broken.
"""
    with open(os.path.join(base_path, "notas_de_elena.txt"), "w", encoding="utf-8") as f:
        f.write(notes)

    # 5. 生成混淆日志
    with open(os.path.join(base_path, "logs/system.log"), "w") as f:
        f.writelines([
            "INFO: System startup at 08:00:00\n",
            "ERROR: Database write failed for TXN_9927 due to unexpected EOF\n",
            "WARNING: Latency detected in transaction gateway\n"
        ])

if __name__ == "__main__":
    build_env()
