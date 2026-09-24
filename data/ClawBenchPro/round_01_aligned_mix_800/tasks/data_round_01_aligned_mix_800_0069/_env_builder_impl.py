import os
import argparse
import json
import random

def build_turn_1():
    # 创建初始复杂的工程目录
    os.makedirs("bids/raw_emails", exist_ok=True)
    os.makedirs("contracts/templates", exist_ok=True)
    os.makedirs("regulatory_standards", exist_ok=True)

    # 1. 监管标准文件 (含有逻辑陷阱)
    standards = {
        "safety_code": "TX-2024-BUILD",
        "mandatory_insurance_min": 500000,
        "material_restriction": ["lead-based-paint", "non-certified-concrete-TypeC"],
        "max_subcontractor_limit": 3
    }
    with open("regulatory_standards/compliance_v1.json", "w") as f:
        json.dump(standards, f, indent=4)

    # 2. 杂乱的电子邮件投标书 (需要解析、计算和逻辑筛选)
    emails = [
        {
            "from": "pete_the_pro@gmail.com",
            "subject": "Foundation bid for Hilltop",
            "body": "Hey man, I can do the foundation for $22,000. I use TypeC concrete (it's fast). My insurance coverage is 600k. Let's roll!"
        },
        {
            "from": "quality_builds_inc@outlook.com",
            "subject": "Hilltop Project Proposal",
            "body": "Formal quote: $28,500. All materials are Grade-A certified. Liability insurance is $1M. We require 30% upfront."
        },
        {
            "from": "fast_track_contractors@tech.com",
            "subject": "Re: Construction bid",
            "body": "Bro, $21,000 flat. Insurance? I got 450k coverage, but we've never had an accident. We use standard Grade-B concrete."
        }
    ]
    for i, email in enumerate(emails):
        with open(f"bids/raw_emails/msg_{i+104}.txt", "w") as f:
            f.write(f"From: {email['from']}\nSubject: {email['subject']}\n\n{email['body']}")

def build_turn_2():
    # 模拟项目进展，增加材料价格波动表
    os.makedirs("market_data", exist_ok=True)
    prices = [
        {"item": "Steel_Beam", "prev_price": 450, "current_price": 580, "unit": "ton"},
        {"item": "Certified_Concrete", "prev_price": 120, "current_price": 145, "unit": "cubic_yard"},
        {"item": "Lumber_2x4", "prev_price": 8, "current_price": 14, "unit": "piece"}
    ]
    with open("market_data/weekly_update.json", "w") as f:
        json.dump(prices, f, indent=4)
    
    # 增加一个新的复杂分包商投标，表面完美但在 turn 3 会冲突
    with open("bids/raw_emails/msg_201.txt", "w") as f:
        f.write("From: eco_structure@green.com\nSubject: Special Offer\n\nI heard you need steel work. $15,000 total, but only if you sign by Friday. We use reclaimed steel, 1M insurance.")

def build_turn_3():
    # 监管规则突变
    os.makedirs("regulatory_standards/updates", exist_ok=True)
    with open("regulatory_standards/updates/emergency_alert.txt", "w") as f:
        f.write("NOTICE: Effective immediately, all 'reclaimed' or 'recycled' structural steel is banned for residential projects under TX-2024-BUILD due to stress-test failures.")

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
