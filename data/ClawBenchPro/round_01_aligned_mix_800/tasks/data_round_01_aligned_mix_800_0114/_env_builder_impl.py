import os
import argparse
import json
import random

def build_turn_1():
    # 建立基础目录结构
    os.makedirs("customer_inquiries", exist_ok=True)
    os.makedirs("shipping_manifests", exist_ok=True)
    os.makedirs("carrier_policies", exist_ok=True)
    
    # 承运商政策文件（包含复杂的阶梯赔偿和免责条款）
    policies = {
        "SwiftLink_Logistics": {
            "base_refund": 0.5, 
            "delay_threshold_hours": 48,
            "fragile_surcharge_refund": False,
            "max_compensation": 500
        },
        "GlobalRoute_Express": {
            "base_refund": 0.8,
            "delay_threshold_hours": 24,
            "fragile_surcharge_refund": True,
            "max_compensation": 300
        }
    }
    with open("carrier_policies/contracts.json", "w") as f:
        json.dump(policies, f, indent=4)

    # 运输清单（包含错误数据和不一致性）
    manifests = [
        {"tracking_id": "SL-101", "carrier": "SwiftLink_Logistics", "status": "Delayed", "delay_hours": 50, "declared_value": 1000, "type": "Fragile"},
        {"tracking_id": "SL-102", "carrier": "SwiftLink_Logistics", "status": "Lost", "delay_hours": 0, "declared_value": 200, "type": "Regular"},
        {"tracking_id": "GR-901", "carrier": "GlobalRoute_Express", "status": "Delayed", "delay_hours": 30, "declared_value": 400, "type": "Fragile"},
        {"tracking_id": "GR-902", "carrier": "GlobalRoute_Express", "status": "Delivered", "delay_hours": 0, "declared_value": 150, "type": "Regular"}
    ]
    with open("shipping_manifests/weekly_log.json", "w") as f:
        json.dump(manifests, f, indent=4)

    # 客户投诉邮件汇总（脏数据：有些单号不存在，有些描述与清单不符）
    complaints = """From: user_a@mail.com | Subject: Where is SL-101? | Body: My fragile vase is 3 days late!
From: user_b@mail.com | Subject: SL-102 gone! | Body: They lost my package. Full refund now.
From: user_c@mail.com | Subject: GR-901 Delay | Body: Late again, and you charged me for fragile handling!
From: user_d@mail.com | Subject: Fake Complaint | Body: I just want a discount on SL-999 (Note: Non-existent ID)."""
    with open("customer_inquiries/active_complaints.txt", "w") as f:
        f.write(complaints)

def build_turn_2():
    # 模拟财务审查介入，增加审计日志和新的限制条件
    os.makedirs("audit_internal", exist_ok=True)
    new_restrictions = {
        "audit_code": "SEC-2023-X",
        "blacklisted_users": ["user_d@mail.com"],
        "max_daily_payout": 600
    }
    with open("audit_internal/restrictions.json", "w") as f:
        json.dump(new_restrictions, f, indent=4)
        
    # 注入新的增量争议
    extra_manifests = [
        {"tracking_id": "GR-905", "carrier": "GlobalRoute_Express", "status": "Delayed", "delay_hours": 72, "declared_value": 800, "type": "Regular"}
    ]
    with open("shipping_manifests/increment_log.json", "w") as f:
        json.dump(extra_manifests, f, indent=4)

def build_turn_3():
    # 最后一轮：突发政策变更，针对之前的记录进行“翻案”
    with open("carrier_policies/amendment.txt", "w") as f:
        f.write("NOTICE: Effective immediately, SwiftLink_Logistics max_compensation reduced to 150 for all retroactive claims filed this week due to force majeure.")

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
