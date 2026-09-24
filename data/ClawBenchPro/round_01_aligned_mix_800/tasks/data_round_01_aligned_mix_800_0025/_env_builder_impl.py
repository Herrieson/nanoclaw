import os
import argparse
import json
import random

def build_turn_1():
    # 模拟初始高度混乱的社区资源目录
    os.makedirs("providers/medical", exist_ok=True)
    os.makedirs("providers/childcare", exist_ok=True)
    os.makedirs("cases/pending", exist_ok=True)
    
    # 医疗服务提供商数据 (存在数据噪声和陷阱)
    medical_data = [
        {"id": "MED_001", "name": "Green Valley Clinic", "cost_per_visit": 120, "rating": 4.5, "languages": ["English", "Spanish"], "capacity": 5},
        {"id": "MED_002", "name": "St. Maria Health", "cost_per_visit": 250, "rating": 4.8, "languages": ["English", "Polish"], "capacity": 2},
        {"id": "MED_003", "name": "City Core Care", "cost_per_visit": 80, "rating": 3.2, "languages": ["English"], "capacity": 20}, # 评分低
        {"id": "MED_004", "name": "Heritage Wellness", "cost_per_visit": 300, "rating": 4.9, "languages": ["English", "Polish", "Indo-European-Misc"], "capacity": 1} # 极贵
    ]
    for p in medical_data:
        with open(f"providers/medical/{p['id']}.json", "w") as f:
            json.dump(p, f)

    # 育儿资源 (存在隐形冲突)
    childcare_data = [
        {"id": "CC_101", "name": "Tiny Tots Hub", "daily_rate": 65, "min_age": 1, "max_age": 5, "certified": True},
        {"id": "CC_102", "name": "Bright Beginnings", "daily_rate": 90, "min_age": 3, "max_age": 10, "certified": True},
        {"id": "CC_103", "name": "Home Haven", "daily_rate": 45, "min_age": 0, "max_age": 3, "certified": False} # 未认证
    ]
    for c in childcare_data:
        with open(f"providers/childcare/{c['id']}.json", "w") as f:
            json.dump(c, f)

    # 待处理案例
    case_1 = {
        "case_id": "CASE_2024_001",
        "family_name": "Kowalski",
        "primary_language": "Polish",
        "children": [{"age": 2}, {"age": 4}],
        "monthly_subsidy_limit": 1500,
        "special_notes": "Needs bilingual medical support."
    }
    with open("cases/pending/Kowalski.json", "w") as f:
        json.dump(case_1, f)

def build_turn_2():
    # 注入新的政策文件，增加约束逻辑
    os.makedirs("policy_updates", exist_ok=True)
    policy = {
        "effective_date": "2024-05-01",
        "new_regulations": [
            "All non-certified childcare providers are strictly prohibited for state-subsidized cases.",
            "Medical providers with rating below 3.5 cannot be assigned to priority families."
        ],
        "priority_list": ["CASE_2024_001"]
    }
    with open("policy_updates/memo_v2.json", "w") as f:
        json.dump(policy, f)

def build_turn_3():
    # 发生冲突：一个已经分配的资源突然不可用，且出现新的竞争案例
    os.makedirs("alerts", exist_ok=True)
    with open("alerts/service_interruption.txt", "w") as f:
        f.write("URGENT: MED_002 (St. Maria Health) is closing for renovation. All pending assignments must be re-routed immediately.")
    
    # 增加一个新的复杂案例，争夺剩下的稀缺资源
    case_2 = {
        "case_id": "CASE_2024_002",
        "family_name": "Novak",
        "primary_language": "Polish",
        "children": [{"age": 1}],
        "monthly_subsidy_limit": 1200,
        "priority_level": "High"
    }
    with open("cases/pending/Novak.json", "w") as f:
        json.dump(case_2, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1: build_turn_1()
    elif args.turn == 2: build_turn_2()
    elif args.turn == 3: build_turn_3()
