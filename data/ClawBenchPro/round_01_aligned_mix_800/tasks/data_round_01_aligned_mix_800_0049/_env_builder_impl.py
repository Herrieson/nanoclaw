import os
import argparse
import json
import random

def build_turn_1():
    # 建立目录结构
    os.makedirs("inventory/scanned_receipts", exist_ok=True)
    os.makedirs("inventory/messy_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 模拟混乱的数据：收据
    receipts = [
        {"item": "Bleach Pro-X", "qty": 50, "price": 15.5, "status": "sealed", "location": "Room 302"},
        {"item": "EcoClean Spray", "qty": 20, "price": 22.0, "status": "opened", "location": "Storage A"},
        {"item": "Industrial Degreaser", "qty": 10, "price": 45.0, "status": "sealed", "location": "Activity Center"},
        {"item": "SoftTouch Hand Soap", "qty": 100, "price": 5.0, "status": "sealed", "location": "Storage B"}
    ]
    with open("inventory/scanned_receipts/receipt_batch_01.json", "w") as f:
        json.dump(receipts, f)

    # 模拟脏数据：手写日志 (csv格式，带些脏字符)
    with open("inventory/messy_logs/daily_log.csv", "w") as f:
        f.write("item_name,quantity,notes\n")
        f.write("Latex Gloves,500,Critical Stock!\n")
        f.write("Bleach Pro-X,5,Damaged box\n")
        f.write("Ammonia Solution,2,DANGEROUS NEAR BLEACH!!!\n")
        f.write("Bird Seeds (Donation),50,For the patio\n")

    # 核心逻辑陷阱：Ammonia Solution 和 Bleach 是不能放在一起的（存放禁忌）
    # 且 Bleach Pro-X 在 Activity Center (老人活动室) 是违反安全规定的

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 增量政策：环保倡议
    with open("updates/policy_change.txt", "w") as f:
        f.write("REVISED POLICY v2024:\n")
        f.write("1. All cleaning agents containing Chlorine or Ammonia are BANNED for future use.\n")
        f.write("2. Return policy: Unopened banned items can be returned for a 80% refund.\n")
        f.write("3. Preferred items: Anything with 'Eco' in name receives a 10% tax credit.\n")

def build_turn_3():
    os.makedirs("audit_request", exist_ok=True)
    # 审计需求：三楼需要紧急补给
    audit_data = {
        "target": "3rd Floor - Dementia Care Unit",
        "requirements": [
            {"item": "Latex Gloves", "min_qty": 600},
            {"item": "SoftTouch Hand Soap", "min_qty": 30},
            {"item": "Sanitizer (Green)", "min_qty": 15}
        ],
        "audit_id": "REQ-9921-X"
    }
    with open("audit_request/urgent.json", "w") as f:
        json.dump(audit_data, f)

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
