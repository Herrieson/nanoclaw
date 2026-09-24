import os
import argparse
import json
import random

def build_turn_1():
    # 初始环境：大量的科研项目申请书，包含预算、合作方和研究计划
    os.makedirs("grant_applications", exist_ok=True)
    os.makedirs("regulatory_frameworks", exist_ok=True)
    os.makedirs("audit_working_papers", exist_ok=True)

    # 政策文件：极其繁琐的合规标准
    policy = {
        "grant_id_prefix": "GLOBAL-2024",
        "max_overhead_rate": 0.15,
        "restricted_entities": ["Vanday Group", "Ouroboros Tech"],
        "max_travel_percentage": 0.10,
        "required_ethical_approvals": ["BioEthics-L1", "DataPrivacy-V2"]
    }
    with open("regulatory_frameworks/standards.json", "w") as f:
        json.dump(policy, f, indent=4)

    # 申请书数据：埋入陷阱
    # 申请1：看似完美，但管理费超标
    app_1 = {
        "id": "GLOBAL-2024-001",
        "title": "Sustainable Water Purification in Rural Gujarat",
        "budget": 500000,
        "breakdown": {"research": 400000, "overhead": 85000, "travel": 15000}, # overhead = 17% > 15%
        "partners": ["IIT Mumbai", "Local NGOs"],
        "ethics": ["BioEthics-L1", "DataPrivacy-V2"]
    }
    # 申请2：使用了受限实体，且隐藏在二级供应商中
    app_2 = {
        "id": "GLOBAL-2024-002",
        "title": "AI-Driven Crop Yield Prediction",
        "budget": 300000,
        "breakdown": {"research": 250000, "overhead": 30000, "travel": 20000}, # travel = 6.6% OK
        "partners": ["Tech University", "Vanday Group"], # Restricted Entity
        "ethics": ["DataPrivacy-V2"] # Missing BioEthics-L1
    }
    # 申请3：边缘合格，但总额巨大，后续轮次会调整
    app_3 = {
        "id": "GLOBAL-2024-003",
        "title": "Genomic Diversity Study - South Asia",
        "budget": 1200000,
        "breakdown": {"research": 1050000, "overhead": 100000, "travel": 50000}, # All OK
        "partners": ["National Health Institute"],
        "ethics": ["BioEthics-L1", "DataPrivacy-V2"]
    }

    for app in [app_1, app_2, app_3]:
        with open(f"grant_applications/{app['id']}.json", "w") as f:
            json.dump(app, f, indent=4)

def build_turn_2():
    # 注入增量冲突：外部黑名单更新，影响原本“合格”的申请 3
    os.makedirs("updates_q2", exist_ok=True)
    blacklist_update = {
        "new_restricted_entities": ["National Health Institute"], # 现在 003 也变违规了
        "reason": "Ethical concerns regarding genomic data sovereignty"
    }
    with open("updates_q2/security_alert.json", "w") as f:
        json.dump(blacklist_update, f, indent=4)

def build_turn_3():
    # 注入紧急财务缩减
    with open("updates_q2/budget_cut.txt", "w") as f:
        f.write("URGENT: Total funding pool reduced by 40%. All previously approved budgets must be slashed, "
                "or lower-priority projects eliminated. Maintain focus on Social Justice impact.")

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
