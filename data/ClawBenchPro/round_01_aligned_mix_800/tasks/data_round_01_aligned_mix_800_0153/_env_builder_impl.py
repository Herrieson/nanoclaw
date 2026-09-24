import os
import argparse
import random
import json

def build_turn_1():
    # 初始混乱环境：库存清单、进货发票、临期规则
    os.makedirs("records/inventory", exist_ok=True)
    os.makedirs("records/invoices", exist_ok=True)
    os.makedirs("policy", exist_ok=True)
    
    # 政策文件：复杂的临期折扣逻辑
    policy_content = """
    STATION #402 OPERATIONAL STANDARDS:
    1. Items within 7 days of expiry MUST be marked down by 40%.
    2. Items within 3 days of expiry MUST be removed from shelves and logged as WASTE.
    3. Beverage stock must never drop below 50 units per SKU.
    4. Tax rate for non-fuel items: 7%.
    """
    with open("policy/general_rules.txt", "w") as f:
        f.write(policy_content)

    # 库存数据：存在脏数据和逻辑冲突
    inventory = [
        {"sku": "COKE_001", "name": "Classic Coke 500ml", "stock": 45, "expiry": "2024-12-25", "price": 2.50}, # 需补货
        {"sku": "MILK_002", "name": "Whole Milk 1L", "stock": 12, "expiry": "2024-05-15", "price": 4.00},    # 假设当前是2024-05-12，需打折
        {"sku": "BREAD_003", "name": "White Bread", "stock": 8, "expiry": "2024-05-13", "price": 3.20},    # 需报废
        {"sku": "CHIP_004", "name": "Potato Chips XL", "stock": 120, "expiry": "2024-08-01", "price": 5.00},
        {"sku": "SAND_005", "name": "Ham Sandwich", "stock": 5, "expiry": "2024-05-12", "price": 6.50},    # 需报废
    ]
    with open("records/inventory/current_stock.json", "w") as f:
        json.dump(inventory, f)

    # 发票：需要核对是否入库
    invoice_1 = "INV-2024-001,COKE_001,100 units,Paid\nINV-2024-002,CHIP_004,50 units,Pending"
    with open("records/invoices/latest_deliveries.csv", "w") as f:
        f.write(invoice_1)

def build_turn_2():
    # 模拟时间流逝与数据增量
    os.makedirs("records/notices", exist_ok=True)
    # 突发通知：物价调整
    with open("records/notices/urgent_price_change.txt", "w") as f:
        f.write("Attention: Due to supply chain issues, all Beverage prices must increase by 15% effective immediately. Exclude items already on markdown.")

def build_turn_3():
    # 审计检查：引入外部合规审计表
    os.makedirs("audit", exist_ok=True)
    audit_form = "Item_SKU,Status,Audit_Result\nCOKE_001,In_Stock,OK\nMILK_002,In_Stock,?\nBREAD_003,Waste,?"
    with open("audit/compliance_check.csv", "w") as f:
        f.write(audit_form)

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
