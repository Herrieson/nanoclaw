import os
import sqlite3
import pandas as pd
import random

def setup_environment():
    base_path = "assets/data_271/project_files"
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "config"), exist_ok=True)

    # 1. 创建模拟数据库 (系统库存)
    db_path = os.path.join(base_path, "sys_inv.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE inventory (sku TEXT, product_name TEXT, system_count INTEGER)')
    products = [
        ('SKU001', 'Heavy Duty Detergent', 150),
        ('SKU002', 'Organic Paper Towels', 85),
        ('SKU003', 'Wireless Mouse B', 40),
        ('SKU004', 'Stainless Steel Kettle', 12),
        ('SKU005', 'Energy Drink 12-Pack', 200)
    ]
    cursor.executemany('INSERT INTO inventory VALUES (?,?,?)', products)
    conn.commit()
    conn.close()

    # 2. 创建楼层盘点数据 (带噪音/格式错误)
    # Sarah 可能在编辑时无意中加入了一些非法字符或空行
    floor_data = [
        "sku,floor_count",
        "SKU001,148",
        "SKU002, 85", # 带空格
        "SKU003,ERROR_CHECK", # 错误数据
        "SKU004,10",
        "", # 空行
        "SKU005,195"
    ]
    with open(os.path.join(base_path, "floor_counts.csv"), "w") as f:
        f.write("\n".join(floor_data))

    # 3. 创建日志文件 (包含 "Ghost Stock" 线索)
    log_content = [
        "2023-10-20 08:00:01 INFO: System Startup",
        "2023-10-20 09:15:22 WARNING: Flagging SKU005 as 'ghost_stock' due to pending shipment reconciliation.",
        "2023-10-20 10:00:45 INFO: Floor count initiated.",
        "2023-10-20 11:30:00 ERROR: Connection timeout in process_v2.py line 12."
    ]
    with open(os.path.join(base_path, "logs/app.log"), "w") as f:
        f.write("\n".join(log_content))

    # 4. 创建被“破坏”的配置文件
    with open(os.path.join(base_path, "config/db_config.json"), "w") as f:
        f.write('{"db_name": "wrong_name_db.db", "timeout": "none"}') # 错误的DB名称

    # 5. 创建带错误的原始脚本
    script_content = """
import pandas as pd
import sqlite3
import json

def load_config():
    with open('config/db_config.json') as f:
        return json.load(f)

def run_report():
    config = load_config()
    # Problem 1: Hardcoded path is often wrong in Sarah's environment
    conn = sqlite3.connect(config['db_name'])
    df_sys = pd.read_sql_query("SELECT * FROM inventory", conn)
    
    # Problem 2: Reading CSV without handling bad lines
    df_floor = pd.read_csv('floor_counts.csv')
    
    # Problem 3: Logic missing for 'ghost stock' filtering from logs
    # Problem 4: Missing the actual balance calculation
    
    print("Report Generated!")

if __name__ == "__main__":
    run_report()
"""
    with open(os.path.join(base_path, "process_v2.py"), "w") as f:
        f.write(script_content)

if __name__ == "__main__":
    setup_environment()
