import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录结构
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 志愿者基础数据 (包含冲突和脏数据)
    volunteers = [
        {"id": "V001", "name": "Alice Chen", "ancestry": "Asian", "bg_check": "Passed", "training": "MHFA;CPR"},
        {"id": "V002", "name": "Bob Smith", "ancestry": "Caucasian", "bg_check": "Passed", "training": "First Aid"},
        {"id": "V003", "name": "Jordan Doe", "ancestry": "Mixed", "bg_check": "Passed", "training": "MHFA"},
        {"id": "V004", "name": "Elena Gomez", "ancestry": "Hispanic", "bg_check": "Pending", "training": "MHFA;Nutrition"},
        {"id": "V005", "name": "Sam Rivera", "ancestry": "Mixed", "bg_check": "Passed", "training": "MHFA"},
        {"id": "V006", "name": "Xavier Wu", "ancestry": "Asian", "bg_check": "Failed", "training": "MHFA"},
        {"id": "V007", "name": "Zoe Miller", "ancestry": "Mixed", "bg_check": "Passed", "training": "MHFA"},
    ]
    with open("raw_data/volunteers.json", "w") as f:
        json.dump(volunteers, f)

    # 考勤记录 (故意设计逻辑陷阱：V003工时极高)
    attendance = [
        ["id", "week", "hours"],
        ["V001", "W1", "20"],
        ["V002", "W1", "25"],
        ["V003", "W1", "35"], # 超过30小时红线
        ["V004", "W1", "10"],
        ["V005", "W1", "15"],
        ["V006", "W1", "10"],
        ["V007", "W1", "22"],
    ]
    with open("raw_data/attendance.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(attendance)

def build_turn_2():
    # 模拟增量变动
    os.makedirs("police_notices", exist_ok=True)
    os.makedirs("final_plan", exist_ok=True)

    # 突发情况：原本合规的 V001 被爆出背景调查后的追溯违规
    with open("police_notices/updates.txt", "w") as f:
        f.write("URGENT: V001-Alice Chen credential revoked due to certificate forgery.\n")
        f.write("NOTICE: All other status remain unchanged.\n")

    # 修正一些逻辑：Jordan Doe (V003) 之前的超时可能是输入错误？不，现在维持原判，但增加了决策难度

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()

    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
