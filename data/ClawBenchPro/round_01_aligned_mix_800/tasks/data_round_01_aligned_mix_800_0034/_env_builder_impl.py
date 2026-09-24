import os
import argparse
import csv
import json

def build_turn_1():
    # 初始库存数据：包含故意设计的重复项和边界价格
    os.makedirs("inventory/raw_data", exist_ok=True)
    inventory = [
        ["Title", "Issue", "Year", "Grade", "Estimated_Value", "Publisher", "Creator_Origin"],
        ["Black Panther", "Vol.1 #1", 1977, 9.2, 1200, "Marvel", "African-American"],
        ["Action Comics", "#252", 1959, 4.5, 800, "DC", "US"], # 应标记为不卖且待修复（1970前且<6.0且>500）
        ["Amazing Spider-Man", "#121", 1973, 8.5, 1500, "Marvel", "US"],
        ["Amazing Spider-Man", "#121", 1973, 5.0, 400, "Marvel", "US"], # 重复项，应去重
        ["Fantastic Four", "#48", 1966, 7.0, 2500, "Marvel", "US"], # 1970前，不卖
        ["Vixen", "Special #1", 1978, 9.4, 300, "DC", "African"], # 寻根专题潜在对象
        ["The Phantom", "#10", 1940, 2.0, 1000, "King", "US"], # 1970前，不卖
    ]
    with open("inventory/raw_data/current_stock.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

    with open("inventory/raw_data/scanned_notes.txt", "w") as f:
        f.write("Note: All 'King' publisher items are super rare, add 20% to the estimated value.\n")
        f.write("Note: 'Black Panther' issues have high emotional value, do not trade even if duplicated.")

def build_turn_2():
    os.makedirs("incoming/batch_v2", exist_ok=True)
    # 新增数据：包含冲突项
    new_batch = [
        ["Title", "Issue", "Year", "Grade", "Estimated_Value", "Publisher", "Creator_Origin"],
        ["Icon", "#1", 1993, 9.8, 450, "Milestone", "African-American"],
        ["Black Panther", "Vol.1 #1", 1977, 9.6, 1500, "Marvel", "African-American"], # 比Turn1的成色更好
        ["Static", "#1", 1993, 9.0, 200, "Milestone", "African-American"],
    ]
    with open("incoming/batch_v2/new_arrivals.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_batch)

    # 市场波动
    market = {
        "Marvel": 1.1, # 涨价
        "DC": 0.9,    # 降价
        "Milestone": 1.5,
        "King": 1.0
    }
    with open("incoming/market_fluctuation.json", "w") as f:
        json.dump(market, f)

def build_turn_3():
    # 版权合规性陷阱
    registry = [
        ["Publisher", "Legal_Status"],
        ["Marvel", "Clear"],
        ["DC", "Clear"],
        ["King", "Disputed"], # 触发封存
        ["Milestone", "Clear"]
    ]
    with open("inventory/legal_registry.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(registry)
    
    os.makedirs("quarantine", exist_ok=True)

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
