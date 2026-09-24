import os
import argparse
import json
import csv
import random

def build_turn_1():
    # 创建目录
    os.makedirs("leads", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("contracts/templates", exist_ok=True)

    # 合规规则
    compliance_rules = {
        "min_credit_score": 650,
        "restricted_industries": ["Gambling", "Cryptocurrency", "Military"],
        "scoring_formula": " (ARPU * Contract_Months) * (Credit_Score / 800) ",
        "risk_weights": {
            "Technology": 1.0,
            "Retail": 0.8,
            "Construction": 0.7,
            "Healthcare": 0.9
        }
    }
    with open("config/compliance_rules.json", "w") as f:
        json.dump(compliance_rules, f, indent=4)

    # 潜在客户数据 (包含干扰项)
    leads = [
        ["company_name", "industry", "credit_score", "ARPU", "months"],
        ["SafeTech", "Technology", 720, 1200, 24],      # 高分
        ["BetFast", "Gambling", 780, 5000, 12],        # 行业红线
        ["OldBuild Co", "Construction", 660, 1500, 36], # 边缘过关
        ["MediCare Plus", "Healthcare", 640, 2000, 24],# 信用分红线 (640 < 650)
        ["UrbanRetail", "Retail", 690, 800, 12],       # 低收益
        ["CloudNine", "Technology", 800, 3000, 12],     # 优质
        ["NanoChips", "Technology", 710, 2500, 24],     # 优质
        ["GlobalArch", "Construction", 670, 4000, 12],  # 优质但行业分低
        ["HealthGen", "Healthcare", 750, 1800, 24],     # 优质
    ]
    with open("leads/initial_leads.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(leads)

    # 合同模板
    with open("contracts/templates/standard_v1.txt", "w") as f:
        f.write("STANDARD TELECOM SERVICE AGREEMENT\nTerm: {months} months\nMonthly Fee: {arpu}")

def build_turn_2():
    # 模拟增量环境
    os.makedirs("updates", exist_ok=True)
    
    # 新的黑名单，包含第一轮中看似优质的 "CloudNine"
    blacklist = [
        ["entity_name", "reason"],
        ["CloudNine", "Export Control Violation"],
        ["ShadowNetwork", "Security Risk"]
    ]
    with open("updates/blacklist_v2.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(blacklist)

def build_turn_3():
    os.makedirs("records", exist_ok=True)
    
    # 冲突日志
    clash_log = [
        "TIMESTAMP | ISSUE",
        "2023-10-27 | GlobalArch existing contract expires 2025. New proposal overlap.",
        "2023-10-28 | UrbanRetail credit re-eval pending."
    ]
    with open("records/history_clash.log", "w") as f:
        f.write("\n".join(clash_log))

    # 最终批次数据
    final_leads = [
        ["company_name", "industry", "credit_score", "ARPU", "months"],
        ["BioFuture", "Healthcare", 710, 2200, 36],
        ["SolidFoundations", "Construction", 655, 3500, 24], # 刚过红线，且有新加保证金
        ["CyberShield", "Technology", 790, 1500, 12],
        ["QuickMart", "Retail", 660, 900, 48],
    ]
    with open("leads/final_batch.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(final_leads)

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
