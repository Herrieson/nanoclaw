import os
import argparse
import json
import csv

def build_turn_1():
    # 创建基础目录
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("finance", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 志愿者数据：包含干扰项（虽然便宜但不合规，或技能不匹配）
    applicants = [
        ["id", "name", "skill", "has_special_edu_exp", "hourly_rate", "background"],
        ["V001", "Alice", "Music", "Yes", "20", "Local"],
        ["V002", "Bob", "Painting", "No", "15", "Minority"], # 缺经验
        ["V003", "Carlos", "Music", "Yes", "22", "Portuguese-Bilingual"],
        ["V004", "Diana", "Dance", "Yes", "30", "Local"], # 太贵
        ["V005", "Elena", "Art Therapy", "Yes", "24", "Hispanic"],
        ["V006", "Fabio", "Music", "Yes", "18", "Local"],
        ["V007", "Gina", "Sculpture", "Yes", "25", "Minority"],
        ["V008", "Helena", "Drama", "No", "12", "Local"],
    ]
    with open("raw_data/applicants.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(applicants)

    # 2. 场地报价：包含阶梯定价和隐蔽条款
    venue_quotes = {
        "Venue_A": {
            "name": "Downtown Community Hall",
            "base_rate_per_hour": 100,
            "tier_logic": "fixed",
            "capacity": 80,
            "ethical_rating": "Low", # 对应第二轮的陷阱
            "hidden_clauses": {"extra_over_100_pax": 0.1, "cancel_fee": 500}
        },
        "Venue_B": {
            "name": "Greenwich Arts Center",
            "base_rate_per_hour": 120,
            "tier_logic": "after_6hrs_double",
            "capacity": 150,
            "ethical_rating": "High",
            "hidden_clauses": {"extra_over_100_pax": 0.2, "cancel_fee": 1000}
        },
        "Venue_C": {
            "name": "Inclusive Space Lab",
            "base_rate_per_hour": 150,
            "tier_logic": "fixed",
            "capacity": 120,
            "ethical_rating": "High",
            "hidden_clauses": {"extra_over_100_pax": 0.05, "cancel_fee": 200}
        }
    }
    with open("finance/venue_quotes.json", "w") as f:
        json.dump(venue_quotes, f, indent=4)

def build_turn_2():
    # 第二轮不需要额外文件，逻辑主要依赖于 Agent 对第一轮 Venue_A 评分的发现
    pass

def build_turn_3():
    # 模拟突发取消
    with open("raw_data/cancellations.txt", "w") as f:
        f.write("URGENT: V001 (Alice) and V006 (Fabio) cannot attend due to schedule conflict.")

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
