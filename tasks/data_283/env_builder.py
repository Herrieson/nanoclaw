import os
import sqlite3
import pandas as pd
import random

def setup_environment():
    base_dir = "assets/data_283"
    os.makedirs(os.path.join(base_dir, "scripts"), exist_ok=True)

    # 1. 创建数据库
    db_path = os.path.join(base_dir, "inventory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY,
            sku TEXT,
            item_name TEXT,
            category TEXT,
            style_tag TEXT,
            stock_quantity INTEGER,
            price REAL
        )
    ''')
    
    # 插入初始数据 (存在错误的数据)
    items = [
        (1, 'BAG-001', 'Classic Leather Tote', 'Premium', 'Timeless', 0, 299.0), # 被错误清零
        (2, 'BAG-002', 'Neon Summer Clutch', 'Standard', 'Trendy', 50, 45.0),
        (3, 'ACC-005', 'Silk Scarf Floral', 'Premium', 'Vintage', 5, 89.0), # 数量应为 45
        (4, 'JKT-010', 'Denim Jacket', 'Standard', 'Casual', 100, 55.0), # 数量应为 88
    ]
    cursor.executemany('INSERT INTO inventory VALUES (?,?,?,?,?,?,?)', items)
    conn.commit()
    conn.close()

    # 2. 创建物理盘点单 (正确的数据)
    physical_data = {
        'sku': ['BAG-001', 'BAG-002', 'ACC-005', 'JKT-010'],
        'actual_quantity': [25, 50, 45, 88] # BAG-001 实际上有25个，ACC-005有45个，JKT-010有88个
    }
    pd.DataFrame(physical_data).to_csv(os.path.join(base_dir, "physical_count_march.csv"), index=False)

    # 3. 创建带有逻辑漏洞的脚本
    script_content = """
import sqlite3
import os

def run_reorder():
    db_path = "../inventory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # BUG: 这里的逻辑错误地认为所有 stock < 10 的 Premium 商品都是过季需要剔除的，将其设为了 0
    # 实际上应该是：只有 Standard 类别的且库存过高的才需要处理
    cursor.execute("UPDATE inventory SET stock_quantity = 0 WHERE category = 'Premium' AND stock_quantity < 10")
    
    # 另一个逻辑错误：补货公式写反了
    # cursor.execute("UPDATE inventory SET stock_quantity = stock_quantity + 50 WHERE stock_quantity < 20")
    
    conn.commit()
    conn.close()
    print("Reorder process completed.")

if __name__ == "__main__":
    run_reorder()
"""
    with open(os.path.join(base_dir, "scripts/auto_reorder.py"), "w") as f:
        f.write(script_content.strip())

    # 4. 创建模拟日志
    log_content = """
2023-10-27 02:00:01 - INFO - Starting auto_reorder.py
2023-10-27 02:00:02 - WARNING - Integrity Check Failed for SKU: BAG-001. Reason: Logic override triggered.
2023-10-27 02:00:02 - DEBUG - Executing: UPDATE inventory SET stock_quantity = 0 WHERE category = 'Premium' AND stock_quantity < 10
2023-10-27 02:00:03 - INFO - Reorder process finished with 1 rows affected erroneously.
"""
    with open(os.path.join(base_dir, "system.log"), "w") as f:
        f.write(log_content.strip())

if __name__ == "__main__":
    setup_environment()
