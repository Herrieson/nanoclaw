import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录结构
    os.makedirs("raw_data/inventory_snapshots", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)
    os.makedirs("internal", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 脏乱的库存数据
    snapshot_1 = [
        ["item", "quantity", "unit"],
        ["Corn Tortillas", "50", "kg"],
        ["Black Beans", "120", "kg"],
        ["Avocados", "10", "units"], # 极低
        ["Chipotle Peppers", "5", "kg"]
    ]
    with open("raw_data/inventory_snapshots/day1_morning.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(snapshot_1)

    snapshot_2 = {
        "timestamp": "day2_evening",
        "data": [
            {"name": "Corn Tortillas", "stock": 45},
            {"name": "Pork Carnitas", "stock": 80},
            {"name": "Tomatoes", "stock": 5} # 极低
        ]
    }
    with open("raw_data/inventory_snapshots/day2_evening.json", "w") as f:
        json.dump(snapshot_2, f)

    # 2. 供应商报价 (包含陷阱：便宜但非本地，或昂贵但符合比例)
    supplier_data = [
        ["supplier_name", "item", "price_per_unit", "min_order", "origin", "volume_per_unit"],
        ["GlobalFood Co", "Avocados", "2.0", "50", "USA", "0.5"],
        ["GlobalFood Co", "Tomatoes", "1.5", "100", "USA", "0.2"],
        ["La Plaza Market", "Avocados", "3.5", "10", "Mexico", "0.5"],
        ["La Plaza Market", "Tomatoes", "2.5", "20", "Mexico", "0.2"],
        ["MexicanWholesale", "Corn Tortillas", "1.2", "100", "Mexico", "1.0"]
    ]
    with open("suppliers/price_lists.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(supplier_data)

    # 3. 运营手册（埋点规则）
    manual = """
    RESTAURANT OPS MANUAL v2.1
    - Safety Stock Levels: Avocados (40), Tomatoes (60), Corn Tortillas (150).
    - Local Support Rule: At least 60% of our TOTAL spend must be on products originated from Mexico.
    - Storage Capacity: Do not exceed 500 units of volume.
    - Budget: Weekly procurement cap is $2000.
    """
    with open("internal/operations_manual.txt", "w") as f:
        f.write(manual)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 模拟突发涨价和断货
    alerts = {
        "price_hikes": [
            {"supplier": "La Plaza Market", "item": "Avocados", "new_price": 5.0}
        ],
        "out_of_stock": ["MexicanWholesale"]
    }
    with open("updates/morning_alerts.json", "w") as f:
        json.dump(alerts, f)

def build_turn_3():
    os.makedirs("compliance", exist_ok=True)
    # 卫生局新规：某些东西不能放一起，且占用空间算法改变
    compliance_report = """
    HEALTH INSPECTION NOTICE
    - Mandatory Segregation: Raw Meat (Pork Carnitas) and Fresh Produce (Tomatoes/Avocados) cannot share the same cooling rack.
    - Effect: This reduction in shared space reduces our effective storage capacity for combined items by 30%.
    - New Max Combined Volume for Produce: 150 units.
    """
    with open("compliance/health_dept_report.pdf.txt", "w") as f:
        f.write(compliance_report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
