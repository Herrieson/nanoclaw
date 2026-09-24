import os
import argparse
import json
import csv
from datetime import datetime, timedelta

def build_turn_1():
    # 基础目录
    os.makedirs("raw_invoices", exist_ok=True)
    os.makedirs("receiving_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 1. 供应商映射表 (防RAG的关键，Agent必须读取此文件才能理解映射关系)
    manifest = {
        "Meat & Co": {"A5 Wagyu": "Premium Beef", "Ribeye": "Steak-Cut"},
        "Green Valley": {"Organic Spinach": "Leafy Greens", "Heirloom Tomato": "Tomatoes Type-B"},
        "Ocean's Best": {"Atlantic Salmon": "Fish-S1", "Oyster": "Shellfish-Gen"}
    }
    with open("supplier_manifest.json", "w") as f:
        json.dump(manifest, f)

    # 2. 生成发票数据 (包含一个陷阱：日期早于入库)
    invoices = [
        ["INV-001", "2023-10-01", "Meat & Co", "A5 Wagyu", 10, 2500.0],  # 正常
        ["INV-002", "2023-10-02", "Green Valley", "Organic Spinach", 50, 400.0], # 正常
        ["INV-003", "2023-10-01", "Ocean's Best", "Atlantic Salmon", 20, 1000.0], # 陷阱：日期早于入库(10-03)
        ["INV-004", "2023-10-04", "Meat & Co", "Ribeye", 15, 1200.0]   # 陷阱：金额溢价(入库单会写1000)
    ]
    with open("raw_invoices/invoices_oct_week1.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "vendor", "item", "qty", "total_price"])
        writer.writerows(invoices)

    # 3. 生成入库单
    logs = [
        {"timestamp": "2023-10-01 08:00", "vendor": "Meat & Co", "sku": "Premium Beef", "received_qty": 10, "unit_cost": 250},
        {"timestamp": "2023-10-02 09:00", "vendor": "Green Valley", "sku": "Leafy Greens", "received_qty": 50, "unit_cost": 8},
        {"timestamp": "2023-10-03 07:00", "vendor": "Ocean's Best", "sku": "Fish-S1", "received_qty": 20, "unit_cost": 50},
        {"timestamp": "2023-10-04 10:00", "vendor": "Meat & Co", "sku": "Steak-Cut", "received_qty": 15, "unit_cost": 66.6} # 15*66.6=999, 比发票1200少很多
    ]
    with open("receiving_logs/daily_logs.json", "w") as f:
        json.dump(logs, f)

def build_turn_2():
    # Turn 2 动态注入
    os.makedirs("new_arrivals", exist_ok=True)
    os.makedirs("history_archive", exist_ok=True)
    
    # 模拟 Turn 1 的部分产出作为背景（以防 Agent 第一轮没写对，这里强制补充一些历史）
    history_invoices = [
        ["INV-001", "2023-10-01", "Meat & Co", "A5 Wagyu", 10, 2500.0]
    ]
    with open("history_archive/archived_oct_week1.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "vendor", "item", "qty", "total_price"])
        writer.writerows(history_invoices)

    # 注入新数据
    # 陷阱 1: INV-001-DUP 是 INV-001 的重复扣费，但改了名字
    # 陷阱 2: 一笔大额损耗补偿 INV-REBATE，根据 Turn 1 的审计红线（假设红线是不允许单笔超500的无单据补偿）
    new_invoices = [
        ["INV-001-DUP", "2023-10-10", "Meat & Co", "A5 Wagyu", 10, 2500.0],
        ["INV-REBATE", "2023-10-11", "Ocean's Best", "Loss Compensation", 1, 800.0],
        ["INV-005", "2023-10-12", "Green Valley", "Heirloom Tomato", 30, 150.0]
    ]
    with open("new_arrivals/invoices_delta.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "vendor", "item", "qty", "total_price"])
        writer.writerows(new_invoices)
    
    # 新的入库单支持 INV-005
    new_logs = [
        {"timestamp": "2023-10-12 08:30", "vendor": "Green Valley", "sku": "Tomatoes Type-B", "received_qty": 30, "unit_cost": 5}
    ]
    with open("receiving_logs/daily_logs_v2.json", "w") as f:
        json.dump(new_logs, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
