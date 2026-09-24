import os
import argparse
import json
import random

def build_turn_1():
    # 初始环境：混乱的库存日志和供应商初筛名单
    os.makedirs("inventory_logs", exist_ok=True)
    os.makedirs("vendor_proposals", exist_ok=True)
    
    # 库存日志：包含脏数据、重复项、计算错误
    logs = [
        {"sku": "SKU-9901", "name": "Basic Tee", "category": "Apparel", "stock": 45, "last_audit": "2023-10-01"},
        {"sku": "SKU-9901", "name": "Basic Tee", "category": "Apparel", "stock": -5, "last_audit": "2023-10-05"}, # 脏数据
        {"sku": "SKU-2022", "name": "Designer Denim", "category": "Fashion", "stock": 12, "last_audit": "2023-10-10"},
        {"sku": "SKU-3055", "name": "Poly-Blend Jacket", "category": "Outerwear", "stock": 8, "last_audit": "2023-10-12"},
        {"sku": "SKU-4001", "name": "Wool Scarf", "category": "Accessories", "stock": 0, "last_audit": "2023-10-15"},
    ]
    with open("inventory_logs/current_stock.json", "w") as f:
        json.dump(logs, f, indent=4)

    # 供应商方案：包含诱人的价格和不同的材质构成
    proposals = {
        "Vendor_A_TexStyle": {
            "quote_id": "V-2023-A",
            "materials": {"synthetic": 0.4, "cotton": 0.6},
            "unit_cost": 12.5,
            "min_order": 500,
            "region": "Overseas",
            "lead_time": "45 days"
        },
        "Vendor_B_AmeriWeave": {
            "quote_id": "V-2023-B",
            "materials": {"synthetic": 0.1, "cotton": 0.9},
            "unit_cost": 18.0,
            "min_order": 100,
            "region": "Domestic (Missouri)",
            "lead_time": "10 days"
        },
        "Vendor_C_GlobalFab": {
            "quote_id": "V-2023-C",
            "materials": {"synthetic": 0.7, "cotton": 0.3},
            "unit_cost": 9.0,
            "min_order": 1000,
            "region": "Overseas",
            "lead_time": "60 days"
        }
    }
    for k, v in proposals.items():
        with open(f"vendor_proposals/{k}.json", "w") as f:
            json.dump(v, f, indent=4)

def build_turn_2():
    # 注入突发的高级管理层指令文件，增加系统复杂性
    os.makedirs("corporate_memos", exist_ok=True)
    memo = (
        "MEMO #8821\n"
        "TO: Store Supervisors\n"
        "FROM: Regional Management\n"
        "SUBJECT: Ethical Sourcing and Synthetic Tax\n"
        "New directive: Starting immediately, any product containing more than 35% synthetic materials "
        "will incur a 25% surcharge on the unit cost. Furthermore, domestic vendors are now prioritized "
        "even if their cost is up to 40% higher than international alternatives."
    )
    with open("corporate_memos/directive_synthetic_tax.txt", "w") as f:
        f.write(memo)

def build_turn_3():
    # 模拟环境演进：之前的一些方案失效，出现新的混合数据
    # 模拟在 vendor_proposals 下增加一个“限时折扣”文件，但其交货期与库存缺口冲突
    os.makedirs("alerts", exist_ok=True)
    alert = {
        "alert_type": "Critical Stockout",
        "impact_skus": ["SKU-3055", "SKU-4001"],
        "required_by": "15 days from now",
        "budget_limit": 5000.0
    }
    with open("alerts/restock_emergency.json", "w") as f:
        json.dump(alert, f, indent=4)

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
