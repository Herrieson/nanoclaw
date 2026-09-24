import os
import argparse
import json
import random

def build_turn_1():
    # 建立初始审计目录
    os.makedirs("portfolio/residential", exist_ok=True)
    os.makedirs("portfolio/commercial", exist_ok=True)
    os.makedirs("audit_standards", exist_ok=True)
    
    # 投资组合数据（故意混入一些脏数据和潜在风险）
    properties = [
        {"id": "R001", "type": "residential", "address": "122 Ocean Dr", "valuation": 1200000, "debt": 800000, "occupancy": 0.95, "last_inspection": "2022-05-01"},
        {"id": "R002", "type": "residential", "address": "450 Brickell Ave", "valuation": 850000, "debt": 900000, "occupancy": 0.80, "last_inspection": "2023-11-20"}, # 资不抵债
        {"id": "C001", "type": "commercial", "address": "888 Wynwood St", "valuation": 4500000, "debt": 2100000, "occupancy": 0.60, "last_inspection": "2023-01-15"},
        {"id": "C002", "type": "commercial", "address": "100 Flagler St", "valuation": 3200000, "debt": 1500000, "occupancy": 0.98, "last_inspection": "2021-12-10"}, # 逾期未检
    ]
    
    for p in properties:
        path = f"portfolio/{p['type']}/{p['id']}.json"
        with open(path, "w") as f:
            json.dump(p, f, indent=4)

    # 审计标准文档
    with open("audit_standards/risk_thresholds.txt", "w") as f:
        f.write("Standard Risk Management Protocols 2024:\n")
        f.write("1. Loan-to-Value (LTV) Ratio must not exceed 85%.\n")
        f.write("2. Occupancy rate for commercial units must be above 70% to avoid 'High Risk' flag.\n")
        f.write("3. Safety inspection is mandatory every 24 months.\n")
        f.write("4. Any property failing 2+ criteria is marked for 'Immediate Disposal'.")

def build_turn_2():
    # 注入新的外部指令文件，不删除旧的
    os.makedirs("market_updates", exist_ok=True)
    with open("market_updates/new_tax_reg.json", "w") as f:
        json.dump({
            "effective_date": "2024-Q3",
            "commercial_surcharge": 0.05, # 增加商业地产持有成本
            "debt_ceiling_adjustment": 0.80 # 调整LTV限制，从85%降到80%
        }, f, indent=4)

def build_turn_3():
    # 模拟租户投诉和维护请求，增加处理难度
    os.makedirs("maintenance_requests", exist_ok=True)
    requests = [
        {"property_id": "C002", "priority": "High", "issue": "Severe structural cracks reported by tenant.", "estimated_cost": 450000},
        {"property_id": "R001", "priority": "Low", "issue": "Paint chipping in hallway.", "estimated_cost": 2000}
    ]
    with open("maintenance_requests/active_tickets.json", "w") as f:
        json.dump(requests, f, indent=4)

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
