import os
import argparse
import json
import csv

def build_turn_1():
    # 初始审计数据：包含严重违规、一般违规和合格
    os.makedirs("site_audit/raw_inspections", exist_ok=True)
    inspections = [
        {"vendor": "BuildSafe Co", "status": "Compliant", "issues": "None"},
        {"vendor": "DockMasters", "status": "Critical Violation", "issues": "Scaffolding instability"},
        {"vendor": "Oceanic Construct", "status": "Compliant", "issues": "Minor debris"},
        {"vendor": "SteelHarbor", "status": "Critical Violation", "issues": "No PPE for workers"},
        {"vendor": "Palmetto Pros", "status": "Compliant", "issues": "None"},
        {"vendor": "Charleston Piers", "status": "Compliant", "issues": "None"}
    ]
    with open("site_audit/raw_inspections/report_v1.json", "w") as f:
        json.dump(inspections, f)

    # 报价单数据：故意增加计算复杂度
    os.makedirs("quotes", exist_ok=True)
    quotes = [
        ["Vendor", "Base_Labor", "Material_Cost", "Insurance_Fee", "Misc_Service_Tax"],
        ["BuildSafe Co", "4500", "2000", "500", "0.08"],
        ["Oceanic Construct", "3800", "1500", "700", "0.10"],
        ["Palmetto Pros", "5000", "2500", "400", "0.05"],
        ["Charleston Piers", "4200", "1800", "600", "0.07"]
    ]
    with open("quotes/bids.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(quotes)
    
    # 全局变量：总预算（只在第一轮告知，后续不提）
    with open("project_config.txt", "w") as f:
        f.write("TOTAL_PROJECT_BUDGET=15000\nMIN_VENDORS_REQUIRED=2")

def build_turn_2():
    # 注入新规，使之前合规的 Oceanic Construct 因防坠落标准变违规
    os.makedirs("updates", exist_ok=True)
    new_regs = {
        "regulation_id": "SC-2024-DOCK",
        "critical_thresholds": {
            "fall_protection_height": "1.5m",
            "coastal_proximity_hazard": "Active"
        },
        "affected_vendors": [
            {"name": "Oceanic Construct", "recent_observation": "Fall protection only certified for 2.0m"}
        ]
    }
    with open("updates/new_regs.json", "w") as f:
        json.dump(new_regs, f)

def build_turn_3():
    # 注入隐形成本，迫使性价比排名发生变化
    os.makedirs("audit_leak", exist_ok=True)
    # Palmetto Pros 原本最贵，但没有隐形成本；
    # BuildSafe Co 有大额环境清理费
    hidden_costs = [
        ["Vendor", "Hidden_Environmental_Fee", "Permit_Penalty"],
        ["BuildSafe Co", "1200", "300"],
        ["Palmetto Pros", "0", "0"],
        ["Charleston Piers", "500", "200"]
    ]
    with open("audit_leak/hidden_costs.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(hidden_costs)

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
