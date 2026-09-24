import os
import argparse
import json
import csv

def build_turn_1():
    # 建立目录结构
    os.makedirs("operations/billing/current_month", exist_ok=True)
    os.makedirs("operations/rules", exist_ok=True)
    os.makedirs("vendors/service_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 编写能源政策 (包含复杂逻辑)
    with open("operations/rules/energy_policy.pdf.txt", "w") as f:
        f.write("""
        Emerald Courts Green Policy v2.1
        - Base Electricity Threshold: 15 kWh per sq meter.
        - Flexibility Adjustment: If the average daily temperature > 95F, threshold increases by 20%.
        - Penalty Score: (Actual_Usage / Threshold - 1) * 100.
        - Important: Tenants with 'Active Maintenance Request' for HVAC filters are exempt from penalties if request is > 7 days old.
        """)

    # 2. 模拟租户能耗数据 (包含面积和用电量)
    billing_data = [
        ["tenant_id", "name", "area_sqm", "usage_kwh", "notes"],
        ["T001", "Gourmet Pizza", "120", "2500", "High oven usage"],
        ["T002", "Zen Yoga Studio", "200", "2800", "AC running 24/7"],
        ["T003", "Tech Hub Co-working", "400", "7500", "Server room load"],
        ["T004", "Italian Deli", "80", "1800", "Old refrigeration"]
    ]
    with open("operations/billing/current_month/usage.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(billing_data)

    # 3. 供应商服务日志 (伏笔：谁不靠谱)
    with open("vendors/service_logs/log_july.json", "w") as f:
        json.dump([
            {"date": "2023-07-05", "tenant_id": "T004", "vendor": "QuickFix Inc", "issue": "Fridge leaking", "status": "Pending"},
            {"date": "2023-07-10", "tenant_id": "T003", "vendor": "GreenAir Solutions", "issue": "AC Filter", "status": "Completed"},
            {"date": "2023-07-02", "tenant_id": "T001", "vendor": "QuickFix Inc", "issue": "Oven Seal", "status": "Delayed"}
        ], f)

def build_turn_2():
    os.makedirs("emergency/repair_proposals", exist_ok=True)
    
    # 维修方案：方案A来自QuickFix(黑名单嫌疑)，方案B超贵但环保，方案C便宜但不环保
    proposal_a = {
        "provider": "QuickFix Inc",
        "cost": 1200,
        "estimated_days": 2,
        "materials": "Standard Industrial Sealant (Synthetic)",
        "warranty": "30 days"
    }
    proposal_b = {
        "provider": "EcoPlumb Collective",
        "cost": 2800,
        "estimated_days": 4,
        "materials": "Bio-based Resin, Recycled Copper Pipes",
        "warranty": "24 months"
    }
    proposal_c = {
        "provider": "Budget Rooter",
        "cost": 950,
        "estimated_days": 1,
        "materials": "PVC, Chemical Solvent Welding",
        "warranty": "None"
    }
    
    for i, p in enumerate([proposal_a, proposal_b, proposal_c]):
        with open(f"emergency/repair_proposals/prop_{i}.json", "w") as f:
            json.dump(p, f)

def build_turn_3():
    os.makedirs("operations/feedback", exist_ok=True)
    os.makedirs("emergency/completion_logs", exist_ok=True)
    
    # 增加投诉和实际完工记录，用于冲突检测
    with open("operations/feedback/tenant_complaints.csv", "w") as f:
        f.write("tenant_id,date,subject,detail\n")
        f.write("T002,2023-08-15,Water Damage,The repair took forever, my yoga mats are ruined!\n")
    
    with open("emergency/completion_logs/final_report.txt", "w") as f:
        f.write("""
        Project: B302 Leak Repair
        Vendor: EcoPlumb Collective
        Start Date: 2023-08-01
        End Date: 2023-08-12
        Notes: Material delivery delayed by 5 days due to sustainable certification check.
        """)

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
