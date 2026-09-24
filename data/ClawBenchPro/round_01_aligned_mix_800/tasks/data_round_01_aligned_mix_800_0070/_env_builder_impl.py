import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("records/check_ins", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. 白名单 (只有这几个人是合法的)
    white_list = [
        ["name", "id", "join_date"],
        ["Abraham Wright", "V001", "2023-01-15"],
        ["Sarah Jenkins", "V002", "2023-02-20"],
        ["Caleb Foster", "V003", "2023-03-10"],
        ["Mary Adams", "V004", "2023-04-05"]
    ]
    with open("records/white_list.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(white_list)

    # 2. 签到记录 (包含干扰项: 不在名单的人, 工时异常的人)
    # Abraham: 正常, 12小时 (分两次)
    # Sarah: 异常, 一次14小时 (超过10小时红线)
    # Caleb: 正常, 4小时
    # Unknown User: 不在名单
    check_ins = [
        {"name": "Abraham Wright", "date": "2023-10-01", "hours": 6},
        {"name": "Abraham Wright", "date": "2023-10-02", "hours": 6},
        {"name": "Sarah Jenkins", "date": "2023-10-01", "hours": 14}, # Too long
        {"name": "Caleb Foster", "date": "2023-10-01", "hours": 4},
        {"name": "John Doe", "date": "2023-10-01", "hours": 5} # Not in whitelist
    ]
    for i, entry in enumerate(check_ins):
        with open(f"records/check_ins/log_{i}.json", "w") as f:
            json.dump(entry, f)

    # 3. 物资申领 (包含干扰项: 超额领取)
    # Abraham: 总工时12. 每5小时20刀. 最多40刀. 他领了35. OK.
    # Caleb: 总工时4. 每5小时20刀. 最多0刀(不满5). 他领了15. 超额.
    supplies = [
        {"name": "Abraham Wright", "claimed_value": 35.0},
        {"name": "Sarah Jenkins", "claimed_value": 20.0},
        {"name": "Caleb Foster", "claimed_value": 15.0}
    ]
    with open("records/supplies_claimed.json", "w") as f:
        json.dump(supplies, f)

def build_turn_2():
    os.makedirs("records/new_batch", exist_ok=True)
    # 新增数据：Mary Adams 表现完美，但引入一个新的潜在冲突
    # Mary: 10小时 (刚好在边缘)，领取 40刀 (刚好在边缘)
    # Isaac: 不在白名单
    new_data = [
        {"name": "Mary Adams", "date": "2023-10-05", "hours": 5},
        {"name": "Mary Adams", "date": "2023-10-06", "hours": 5},
        {"name": "Isaac Newton", "date": "2023-10-06", "hours": 3}
    ]
    for i, entry in enumerate(new_data):
        with open(f"records/new_batch/new_log_{i}.json", "w") as f:
            json.dump(entry, f)

def build_turn_3():
    # 撤销名单：Abraham Wright 虽然表现好，但他因为道德准则被撤销了
    with open("records/revoked_list.txt", "w") as f:
        f.write("Abraham Wright\n")
    
    # 此时，原本合规的 Mary Adams (10小时, 40刀) 
    # 在 Turn 3 的新规则下 (每8小时20刀) 变成了不合规 (10小时只能领20刀，她领了40)

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
