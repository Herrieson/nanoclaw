import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录结构
    os.makedirs("customer_data/pending_disputes", exist_ok=True)
    os.makedirs("regulations", exist_ok=True)
    os.makedirs("logs/meter_readings", exist_ok=True)
    
    # 阶梯电价规则：这是一个陷阱。如果不仔细看，会漏掉超额部分的累进逻辑
    pricing_policy = (
        "2024 Summer Pricing Policy (Effective June 1st):\n"
        "Residential (Type-R):\n"
        "- Base: $0.12/kWh (up to 500 kWh)\n"
        "- Peak: $0.25/kWh (above 500 kWh)\n"
        "Commercial (Type-C):\n"
        "- Flat: $0.18/kWh (up to 1000 kWh)\n"
        "- Heavy Duty: $0.35/kWh (above 1000 kWh)\n"
        "Note: All disputes must be calculated based on the net usage after a 5% system loss deduction."
    )
    with open("regulations/pricing_policy.txt", "w") as f:
        f.write(pricing_policy)

    # 生成争议客户数据
    disputes = [
        {"id": "C-101", "type": "Residential", "claimed_amount": "120.00"},
        {"id": "C-102", "type": "Commercial", "claimed_amount": "250.00"},
        {"id": "C-103", "type": "Residential", "claimed_amount": "80.00"},
        {"id": "C-104", "type": "Commercial", "claimed_amount": "500.00"}
    ]
    for d in disputes:
        with open(f"customer_data/pending_disputes/{d['id']}.json", "w") as f:
            json.dump(d, f)

    # 生成原始电量日志数据
    # C-101: 实际用电 800kWh. 
    # 计算逻辑: 800 * 0.95 = 760kWh. 
    # 500*0.12 + 260*0.25 = 60 + 65 = 125. 
    # 原系统可能按非阶梯算了 800 * 0.25 = 200. 应退 75.
    readings = [
        "timestamp,customer_id,reading_kwh\n",
        "2024-06-01,C-101,800\n",
        "2024-06-01,C-102,1200\n",
        "2024-06-01,C-103,400\n",
        "2024-06-01,C-104,2200\n"
    ]
    with open("logs/meter_readings/june_usage.csv", "w") as f:
        f.writelines(readings)

def build_turn_2():
    os.makedirs("audit_notices", exist_ok=True)
    # 标记谁有过延期支付记录
    # C-101 (有延期 -> 只能给信用)
    # C-102 (无延期 -> 现金)
    # C-104 (有延期 -> 只能给信用)
    audit_data = [
        ["customer_id", "delinquency_history", "risk_level"],
        ["C-101", "YES", "Medium"],
        ["C-102", "NO", "Low"],
        ["C-103", "NO", "Low"],
        ["C-104", "YES", "High"]
    ]
    with open("audit_notices/payment_history_flags.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(audit_data)

def build_turn_3():
    os.makedirs("customer_data/profiles_extended", exist_ok=True)
    # 增加行业描述，用于最后的补贴判断
    # C-102 是商业客户，且是“Art Gallery”，命中 15% 补贴
    profiles = [
        {"id": "C-101", "name": "John Doe", "industry": "Residential"},
        {"id": "C-102", "name": "Lagos Expressions Gallery", "industry": "Art & Culture - Studio"},
        {"id": "C-103", "name": "Mary Smith", "industry": "Residential"},
        {"id": "C-104", "name": "Heavy Metal Corp", "industry": "Manufacturing"}
    ]
    for p in profiles:
        with open(f"customer_data/profiles_extended/{p['id']}_profile.json", "w") as f:
            json.dump(p, f)

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
