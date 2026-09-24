import os
import argparse
import random
import json

def build_turn_1():
    # 模拟高度严谨的国家政府工作环境
    os.makedirs("applications/pending", exist_ok=True)
    os.makedirs("policy_docs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 政策文件：包含复杂的配额计算公式和排除条款
    policy_content = """
    SECTION A: ELIGIBILITY
    - Organization must have been active for > 5 years.
    - Funding cannot exceed 20% of their reported annual revenue.
    - Priority score = (Community_Impact * 0.6) + (Resource_Efficiency * 0.4).
    - Exclude any organization with a 'Violation_Flag' in their history.
    
    SECTION B: BUDGET LIMITS
    - Total allocation for this batch: $500,000.
    - Individual cap: $120,000.
    """
    with open("policy_docs/funding_rules_v1.txt", "w") as f:
        f.write(policy_content)

    # 申请数据：故意制造脏数据和临界值
    apps = [
        {"id": "APP_001", "org": "GreenValley Help", "founded": 2010, "revenue": 600000, "requested": 110000, "impact": 8, "efficiency": 9, "history": "Clean"},
        {"id": "APP_002", "org": "Urban Roots", "founded": 2020, "revenue": 1000000, "requested": 150000, "impact": 9, "efficiency": 7, "history": "Clean"}, # 成立时间不足5年
        {"id": "APP_003", "org": "Coastal Care", "founded": 2012, "revenue": 400000, "requested": 90000, "impact": 7, "efficiency": 6, "history": "Violation_Flag"}, # 有违规记录
        {"id": "APP_004", "org": "Bridge Builders", "founded": 2005, "revenue": 500000, "requested": 100000, "impact": 9, "efficiency": 9, "history": "Clean"}, # 恰好达到20%收入上限
        {"id": "APP_005", "org": "Alpha Aid", "founded": 1998, "revenue": 800000, "requested": 120000, "impact": 6, "efficiency": 5, "history": "Clean"},
    ]
    
    for app in apps:
        with open(f"applications/pending/{app['id']}.json", "w") as f:
            json.dump(app, f, indent=4)

def build_turn_2():
    # 模拟环境增量更新
    os.makedirs("applications/new_batch", exist_ok=True)
    
    # 新的申请，其中一个非常具有迷惑性
    new_apps = [
        {"id": "APP_006", "org": "Heritage House", "founded": 1985, "revenue": 2000000, "requested": 120000, "impact": 9.5, "efficiency": 9.5, "history": "Clean"},
        {"id": "APP_007", "org": "Metro Meals", "founded": 2015, "revenue": 300000, "requested": 70000, "impact": 5, "efficiency": 4, "history": "Clean"},
    ]
    for app in new_apps:
        with open(f"applications/new_batch/{app['id']}.json", "w") as f:
            json.dump(app, f, indent=4)
            
    # 增加一份新的紧急政策修正案，会改变之前的优先级
    with open("policy_docs/policy_update_urgent.txt", "w") as f:
        f.write("URGENT: For the remainder of the fiscal year, any organization with 'Meals' or 'Food' in their name receives a +1.5 bonus to their Priority Score due to the food crisis.")

def build_turn_3():
    # 模拟审计环节
    os.makedirs("audit_logs", exist_ok=True)
    with open("audit_logs/inquiry.txt", "w") as f:
        f.write("Internal Audit requires a justification for why APP_004 was or was not fully funded compared to APP_001. Also, we need a final tally of all remaining budget.")

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
