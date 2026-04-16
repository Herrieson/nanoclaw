import os
import sqlite3
import random

def setup_environment():
    base_path = "assets/data_202"
    storage_path = os.path.join(base_path, "storage")
    os.makedirs(storage_path, exist_ok=True)

    # 1. 创建损坏/待恢复的 SQLite 数据库
    db_path = os.path.join(storage_path, "inventory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE parts (
        id INTEGER PRIMARY KEY,
        part_name TEXT,
        brand_origin TEXT,
        part_type TEXT,
        stock_level INTEGER
    )''')
    
    parts_data = [
        (1, 'Bosch Elite Pads', 'German', 'Brake Pads', 15),
        (2, 'Brembo Sport Kit', 'Italian', 'Brake Pads', 5),
        (3, 'Mann Filter A7', 'German', 'Oil Filter', 40),
        (4, 'Zimmermann Rotors', 'German', 'Brake Pads', 8),
        (5, 'Textar Standard', 'German', 'Brake Pads', 2)
    ]
    cursor.executemany('INSERT INTO parts VALUES (?,?,?,?,?)', parts_data)
    conn.commit()
    conn.close()

    # 模拟 WAL 模式下的未提交状态（通过在目录下放一个不完整的 WAL 文件或特定的标记文件，这里通过逻辑注入）
    # 在本任务中，我们将故意在脚本中留下一个逻辑错误来模拟“损坏”
    
    # 2. 创建带有 Bug 的 Python 脚本
    buggy_script = """
import sqlite3

def process_emergency_order(part_id, quantity):
    conn = sqlite3.connect('storage/inventory.db')
    cursor = conn.cursor()
    # BUG: 直接相减没有检查，且由于技师随手写的类型转换可能触发错误逻辑
    cursor.execute("SELECT stock_level FROM parts WHERE id=?", (part_id,))
    current = cursor.fetchone()[0]
    
    # 模拟一个溢出 Bug：如果是紧急订单(quantity > 100)，他误用了一个位移操作
    if quantity > 100:
        new_stock = current - (quantity << 1) # 错误逻辑
    else:
        new_stock = current - quantity
        
    cursor.execute("UPDATE parts SET stock_level=? WHERE id=?", (new_stock, part_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # 假设这里被错误触发了一次
    process_emergency_order(4, 120) 
"""
    with open(os.path.join(base_path, "process_orders.py"), "w") as f:
        f.write(buggy_script)

    # 3. 创建手工维修日志 (service_logs.txt)
    logs = """
    2023-10-24: Installed 4 Zimmermann Rotors on a Porsche 911. (Manual override needed)
    2023-10-25: Used 2 Textar Standard pads for a customer.
    2023-10-25: Received 10 Bosch Elite Pads from supplier.
    """
    with open(os.path.join(base_path, "service_logs.txt"), "w") as f:
        f.write(logs)

if __name__ == "__main__":
    setup_environment()
