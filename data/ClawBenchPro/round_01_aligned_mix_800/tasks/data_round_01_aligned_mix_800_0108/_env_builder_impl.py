import os
import argparse
import json
import random

def build_turn_1():
    # 初始案件库：包含极其琐碎的理赔单据、维修厂报价和医疗证明
    os.makedirs("claims/active", exist_ok=True)
    os.makedirs("policy_database", exist_ok=True)
    os.makedirs("investigation_notes", exist_ok=True)
    
    # 保单政策：非常复杂，包含各种排除条款
    policy = {
        "policy_id": "POL-99283",
        "holder": "Arthur Morgan",
        "coverage_limit": 500000,
        "exclusions": ["Pre-existing mechanical failure", "Racing activities", "Unlicensed drivers"],
        "deductible": 2500,
        "special_clauses": {
            "luxury_parts_cap": 5000,
            "regional_adjustment_factor": 1.15
        }
    }
    with open("policy_database/POL-99283.json", "w") as f:
        json.dump(policy, f, indent=4)

    # 理赔文件：混入了一些逻辑矛盾
    claim_data = {
        "claim_id": "CLM-4402",
        "incident_date": "2023-11-12 23:45",
        "location": "Thunder Canyon Road",
        "description": "Lost control during heavy rain, hit a barrier.",
        "repair_estimates": [
            {"item": "Engine block", "cost": 12000, "vendor": "SpeedyFix Garage"},
            {"item": "Carbon fiber hood", "cost": 8500, "vendor": "SpeedyFix Garage"}, # 触发 luxury_parts_cap
            {"item": "Labor", "cost": 3000, "vendor": "SpeedyFix Garage"}
        ],
        "witness_statements": [
            {"name": "John Marston", "statement": "The car was moving extremely fast, sounded like a race engine."} # 暗示 Racing activities
        ]
    }
    with open("claims/active/CLM-4402_dossier.json", "w") as f:
        json.dump(claim_data, f, indent=4)

def build_turn_2():
    # 模拟外部调查数据的延迟到达
    os.makedirs("external_intelligence", exist_ok=True)
    # 提供一份模糊的社交媒体记录，增加难度
    social_media = [
        {"timestamp": "2023-11-12 22:10", "user": "Artie_M", "post": "Ready to push the limits at the Midnight Sprint tonight! #ThunderCanyon"},
        {"timestamp": "2023-11-12 23:55", "user": "Artie_M", "post": "Bad luck tonight. Car is totaled."}
    ]
    with open("external_intelligence/social_monitor_export.json", "w") as f:
        json.dump(social_media, f, indent=4)
    
    # 增加另一个干扰案件
    os.makedirs("claims/pending_verification", exist_ok=True)
    new_claim = {
        "claim_id": "CLM-5509",
        "incident_date": "2023-12-01",
        "description": "Fender bender in parking lot.",
        "repair_estimates": [{"item": "Bumper", "cost": 800, "vendor": "City Auto"}]
    }
    with open("claims/pending_verification/CLM-5509.json", "w") as f:
        json.dump(new_claim, f, indent=4)

def build_turn_3():
    # 突发法律规则更新（来自合规部）
    os.makedirs("compliance_updates", exist_ok=True)
    regulation = {
        "directive": "2024-FRAUD-01",
        "effective_immediately": True,
        "rule": "Any claim involving 'performance-enhanced' parts mentioned in social media or witness statements must be escalated to the Special Investigation Unit (SIU) regardless of the cost cap."
    }
    with open("compliance_updates/memo_jan_2024.json", "w") as f:
        json.dump(regulation, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1: build_turn_1()
    elif args.turn == 2: build_turn_2()
    elif args.turn == 3: build_turn_3()
