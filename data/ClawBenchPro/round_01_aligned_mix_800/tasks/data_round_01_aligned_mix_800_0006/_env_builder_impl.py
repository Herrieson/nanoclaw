import os
import argparse
import json
import csv

def build_turn_1():
    # 基础目录
    os.makedirs("raw_inputs/vendors", exist_ok=True)
    os.makedirs("compliance_docs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商数据：包含价格、类别和陷阱
    vendors = [
        {"id": "V001", "name": "GreenValley_Events", "category": "Venue", "price": 25000, "note": "Premium space"},
        {"id": "V002", "name": "CheapSpace_Co", "category": "Venue", "price": 15000, "note": "Basic gym"},
        {"id": "V003", "name": "HealthyBites_Catering", "category": "Catering", "price": 8000, "note": "Organic food"},
        {"id": "V004", "name": "FastFood_King", "category": "Catering", "price": 5000, "note": "High calorie"},
        {"id": "V005", "name": "SafeGuard_Security", "category": "Security", "price": 6000, "note": "Certified"},
        {"id": "V006", "name": "WatchMen_Inc", "category": "Security", "price": 4000, "note": "No clear record"},
        {"id": "V007", "name": "EduDisplay_Global", "category": "Display", "price": 7000, "note": "Professional shelves"},
        {"id": "V008", "name": "ScrapWood_Crafts", "category": "Display", "price": 3000, "note": "DIY style"}
    ]
    
    with open("raw_inputs/vendors/price_list.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "price", "note"])
        writer.writeheader()
        writer.writerows(vendors)

    # 合规性文件陷阱：CheapSpace_Co (V002) 缺少背景调查
    # WatchMen_Inc (V006) 资质文件已过期
    # EduDisplay_Global (V007) 完美
    # HealthyBites_Catering (V003) 完美
    compliance = {
        "V001": {"background_check": "Passed", "insurance": "Valid"},
        "V002": {"background_check": "Missing", "insurance": "Valid"},
        "V003": {"background_check": "Passed", "insurance": "Valid"},
        "V004": {"background_check": "N/A", "insurance": "Valid"},
        "V005": {"background_check": "Passed", "insurance": "Valid"},
        "V006": {"background_check": "Passed", "insurance": "Expired"},
        "V007": {"background_check": "Passed", "insurance": "Valid"},
        "V008": {"background_check": "Failed", "insurance": "Valid"}
    }
    
    for v_id, status in compliance.items():
        with open(f"compliance_docs/{v_id}_cert.json", "w") as f:
            json.dump(status, f)

    # 初始赞助商信息
    sponsorship = {"confirmed_funding": 10000, "internal_budget": 35000} # 总 45000
    with open("raw_inputs/budget_limit.json", "w") as f:
        json.dump(sponsorship, f)

def build_turn_2():
    os.makedirs("turn_2_updates", exist_ok=True)
    # 新增需求，迫使 Agent 重新平衡预算
    new_reqs = {
        "reading_corner": {
            "required_items": ["Bookshelves", "SoftMats"],
            "estimated_cost": 4000,
            "priority": "High"
        },
        "media_reception": {
            "item": "PressKit_and_Refreshments",
            "estimated_cost": 2500,
            "priority": "Medium"
        }
    }
    with open("turn_2_updates/new_requests.json", "w") as f:
        json.dump(new_reqs, f)
    
    # 增加一个备选廉价供应商，但有潜在合规风险
    with open("turn_2_updates/backup_vendors.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "category", "price", "note"])
        writer.writerow(["V009", "QuickBuild_Displays", "Display", 4500, "Refurbished"])
    
    with open("compliance_docs/V009_cert.json", "w") as f:
        json.dump({"background_check": "Passed", "insurance": "Valid"}, f)

def build_turn_3():
    os.makedirs("audit_notices", exist_ok=True)
    # 剧情杀：原本合规的 V003 (HealthyBites) 餐饮公司因为最近的一次事故被撤销了保险资质
    with open("audit_notices/warning_log.txt", "w") as f:
        f.write("AUDIT ALERT: 2023-Q4 Compliance Review\n")
        f.write("Critical Issue: Vendor V003 (HealthyBites_Catering) insurance policy flagged as REVOKED by state regulator.\n")
        f.write("Action Required: Replace vendor immediately to maintain event permit.")

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
