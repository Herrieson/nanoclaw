import os
import sqlite3
import json
import random
from datetime import datetime, timedelta

def setup_environment():
    base_path = "assets/data_315"
    os.makedirs(os.path.join(base_path, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "database"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "contracts"), exist_ok=True)

    # 1. 模拟废油传感器日志 (Deep Fryer Sensors)
    # 逻辑： fryer_id, usage_hours, estimated_waste_rate (L/h)
    log_file = os.path.join(base_path, "logs/fryer_sensors.log")
    with open(log_file, "w") as f:
        f.write("timestamp,fryer_id,temp_c,usage_hours\n")
        start_date = datetime(2023, 10, 2) # A Monday
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            for fryer in ["FRY_A", "FRY_B"]:
                hours = round(random.uniform(5.0, 8.0), 2)
                f.write(f"{current_date.strftime('%Y-%m-%d')},{fryer},180,{hours}\n")

    # 2. 模拟回收桶重量记录 (SQLite)
    db_path = os.path.join(base_path, "database/disposal.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE waste_collection (date TEXT, actual_weight_kg REAL)")
    # 设定：理论产生 = hours * 1.5kg/h。
    # 故意制造周三和周五的异常：周三少记录了5kg，周五少记录了8kg
    waste_data = [
        ("2023-10-02", 20.5), # Mon
        ("2023-10-03", 19.8), # Tue
        ("2023-10-04", 5.2),  # Wed (High deviation! Theoretical ~20)
        ("2023-10-05", 21.0), # Thu
        ("2023-10-06", 4.1),  # Fri (High deviation! Theoretical ~20)
        ("2023-10-07", 10.5), # Sat
        ("2023-10-08", 9.8),  # Sun
    ]
    cursor.executemany("INSERT INTO waste_collection VALUES (?, ?)", waste_data)
    conn.commit()
    conn.close()

    # 3. 供应商合同与采购记录 (JSON)
    # 州：Minnesota (MN)
    vendors = [
        {"id": "V001", "name": "Twin Cities Organic", "state": "MN", "green_certified": True},
        {"id": "V002", "name": "Deep South Logistics", "state": "GA", "green_certified": False},
        {"id": "V003", "name": "North Star Greens", "state": "MN", "green_certified": True},
        {"id": "V004", "name": "Sysco Bulk", "state": "TX", "green_certified": False}
    ]
    with open(os.path.join(base_path, "contracts/vendors.json"), "w") as f:
        json.dump(vendors, f)

    purchases = [
        {"date": "2023-10-02", "vendor_id": "V001", "amount": 1200.0},
        {"date": "2023-10-03", "vendor_id": "V004", "amount": 3500.0},
        {"date": "2023-10-04", "vendor_id": "V002", "amount": 2800.0},
        {"date": "2023-10-05", "vendor_id": "V003", "amount": 1500.0},
        {"date": "2023-10-06", "vendor_id": "V004", "amount": 4000.0},
    ]
    with open(os.path.join(base_path, "contracts/purchases_oct_week1.json"), "w") as f:
        json.dump(purchases, f)

    # 常数参考文件（Astrid 的笔记）
    with open(os.path.join(base_path, "astrid_notes.txt"), "w") as f:
        f.write("Note: Each hour of fryer usage should result in 1.5kg of waste oil.\n")
        f.write("Local MN vendors must be green_certified to count towards the 50% goal.\n")

if __name__ == "__main__":
    setup_environment()
