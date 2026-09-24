import os
import csv
import random

def build_env():
    # 创建目录
    os.makedirs("facility_logs", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 生成乱七八糟的日志数据
    log_files = ["monday_shift.csv", "midweek_notes.txt", "friday_final.csv"]
    
    # 模拟数据：日期, 房间号, 物品, 消耗量
    # 场景1：存在领了Bleach但房间为空的记录 (流失记录)
    log_content_1 = [
        ["Date", "Room", "Item", "Used"],
        ["2023-12-01", "Room 101", "Bleach", "2"],
        ["2023-12-01", "", "Bleach", "1"],  # 异常项 1
        ["2023-12-02", "Room 102", "Soap", "5"]
    ]
    
    with open("facility_logs/monday_shift.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_content_1)

    # 杂乱的文本日志
    with open("facility_logs/midweek_notes.txt", "w") as f:
        f.write("2023-12-03: Used 3 units of Bleach but forgot the room number.\n") # 异常项 2
        f.write("2023-12-04: Room 105 used 1 unit of Bleach.\n")

    # 最后的CSV
    log_content_2 = [
        ["Date", "Room", "Item", "Used"],
        ["2023-12-05", "Room 108", "Bleach", "2"],
        ["2023-12-05", "Room 110", "Soap", "3"]
    ]
    with open("facility_logs/friday_final.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_content_2)

    # 库存数据
    # Bleach 总消耗应为: 2(Mon) + 1(Mon_Missing) + 3(Mid_Missing) + 1(Mid) + 2(Fri) = 9
    # 假设库存减少了 7，那么有 2 个差额
    inventory_data = [
        ["Item", "Start_Stock", "End_Stock"],
        ["Bleach", "50", "43"],
        ["Soap", "100", "92"]
    ]
    with open("inventory/weekly_inventory.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

if __name__ == "__main__":
    build_env()
