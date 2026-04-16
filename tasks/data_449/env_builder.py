import os
import json
import sqlite3
import random

def setup_environment():
    base_path = "assets/data_449"
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(f"{base_path}/old_logs", exist_ok=True)
    os.makedirs(f"{base_path}/personal_notes", exist_ok=True)
    os.makedirs(f"{base_path}/scripts/backup", exist_ok=True)

    # 1. 模拟一个损坏的数据库
    db_path = f"{base_path}/agency_records.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE services (family_id TEXT, amount REAL, priority TEXT, date TEXT)")
    
    # 插入一些基础数据 (部分符合要求，部分不符合)
    data = [
        ('FAM-001', 300.50, 'High', '2023-05-12'),
        ('FAM-002', 600.00, 'Low', '2023-06-15'),
        ('FAM-003', 450.00, 'High', '2023-01-20'),
        ('FAM-004', 1200.00, 'High', '2023-11-05')
    ]
    cursor.executemany("INSERT INTO services VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

    # 2. 模拟由于 low conscientiousness 导致的混乱：散落在日志中的补充数据
    log_content = """
    2023-08-10: Processed transaction for FAM-001. Additional emergency fund approved: $250.
    2023-09-12: Error in DB for FAM-005. Manual entry: Amount $750, Priority High. 
    2023-10-01: System reboot...
    """
    with open(f"{base_path}/old_logs/syslog_aug_oct.log", "w") as f:
        f.write(log_content)

    # 3. 模拟文学笔记中的关键碎片 (隐藏的陷阱和必要数据)
    notes = """
    "Quiet as it's kept, there were no marigolds in the fall of 1941." - Toni Morrison.
    
    Note to self: The grant auditor said FAM-003 should be boosted by $100 because of the winter heating crisis. 
    Also, FAM-006 reached out. Total assistance: $900, Priority: High. Need to add this to the XML later!
    Must finish reading the chapter before the meeting at 3 PM.
    """
    with open(f"{base_path}/personal_notes/reading_reflections.txt", "w") as f:
        f.write(notes)

    # 4. 模拟一个写了一半的、有 Bug 的脚本
    broken_script = """
import sqlite3
# I think I need to sum the amounts for each family_id...
# But I got distracted by a new book.
def get_data():
    conn = sqlite3.connect('../agency_records.db')
    # cursor = conn.execute("SELECT * FROM services") # TODO: finish this
    pass
    """
    with open(f"{base_path}/scripts/data_tool.py", "w") as f:
        f.write(broken_script)

if __name__ == "__main__":
    setup_environment()
