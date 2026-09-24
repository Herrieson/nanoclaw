import os
import argparse
import json
import csv
import random

def build_turn_1():
    os.makedirs("raw_archives", exist_ok=True)
    os.makedirs("processing_state", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 原始病历数据 (混合干扰项)
    records = [
        {"pid": "AZ-10001", "dept": "Cardiology", "fund": "Private", "amount": 1200, "blood": "A+", "allergies": "None"},
        {"pid": "AZ-10002", "dept": "Radiology", "fund": "State_Funded", "amount": 6000, "blood": "B-", "allergies": "Peanuts"}, # 需脱敏
        {"pid": "BAD-99", "dept": "General", "fund": "Private", "amount": 500, "blood": "O+", "allergies": "None"}, # 格式错误
        {"pid": "AZ-10003", "dept": "Neurology", "fund": "State_Funded", "amount": 3000, "blood": "AB+", "allergies": "Sulfa"}, # 合规
        {"pid": "AZ-10004", "dept": "Radiology", "fund": "Private", "amount": 8000, "blood": "O-", "allergies": "None"},
    ]
    with open("raw_archives/records_batch_1.json", "w") as f:
        json.dump(records, f)

    # 访问日志 (含违规)
    with open("raw_archives/access_logs.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["pid", "timestamp", "user"])
        writer.writerow(["AZ-10001", "2023-10-01 10:00", "dr_smith"])
        writer.writerow(["AZ-10002", "2023-10-01 23:00", "night_shift_admin"]) # 潜在违规
        writer.writerow(["AZ-10004", "2023-10-02 02:00", "unknown_guest"]) # 潜在违规

    # 授权表
    with open("raw_archives/authorization_forms.json", "w") as f:
        json.dump([{"pid": "AZ-10002", "auth_by": "Director_Admin"}], f) # 10002有授权, 10004没有

def build_turn_2():
    os.makedirs("incremental_batch", exist_ok=True)
    
    # 增量数据：故意引入Radiology + State_Funded (触发新规则)
    new_records = [
        {"pid": "AZ-10005", "dept": "Radiology", "fund": "State_Funded", "amount": 2000, "blood": "A-", "allergies": "Pollen"}, # 新规则下需脱敏
        {"pid": "AZ-10001", "dept": "Cardiology", "fund": "Private", "amount": 1500, "blood": "A+", "allergies": "None"}, # 重复PID，检查一致性用
    ]
    with open("incremental_batch/records_batch_2.json", "w") as f:
        json.dump(new_records, f)
    
    # 追溯授权：解决之前10004的锁定问题
    with open("incremental_batch/retroactive_auth.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["pid", "retro_code", "approver"])
        writer.writerow(["AZ-10004", "AUTH-992", "Board_Member_X"])

def build_turn_3():
    # 最终轮：引入数据冲突（数据一致性陷阱）
    os.makedirs("final_check", exist_ok=True)
    conflict_data = [
        {"pid": "AZ-10003", "dept": "Neurology", "fund": "State_Funded", "amount": 4500, "blood": "O+", "allergies": "Sulfa"} # 与第一轮10003的血型(AB+)冲突
    ]
    with open("final_check/late_arrivals.json", "w") as f:
        json.dump(conflict_data, f)

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
