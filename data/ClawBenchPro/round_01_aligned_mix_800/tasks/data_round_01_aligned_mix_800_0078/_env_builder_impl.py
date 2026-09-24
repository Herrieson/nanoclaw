import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("store_data/inventory", exist_ok=True)
    os.makedirs("store_data/orders", exist_ok=True)
    os.makedirs("store_data/staff", exist_ok=True)

    # 库存数据 (陷阱：Item_101 总库存很大，但环保认证的只有 50；Item_102 无认证)
    inventory_data = [
        {"item_id": "ITM_101", "name": "Pine_Wood_Planks", "total_qty": "500", "eco_certified_qty": "50"},
        {"item_id": "ITM_102", "name": "Standard_Paint_White", "total_qty": "1000", "eco_certified_qty": "0"},
        {"item_id": "ITM_103", "name": "Eco_Sealant_Pro", "total_qty": "200", "eco_certified_qty": "200"},
        {"item_id": "ITM_104", "name": "Steel_Beams", "total_qty": "80", "eco_certified_qty": "0"},
        {"item_id": "ITM_105", "name": "Low_VOC_Paint_Blue", "total_qty": "300", "eco_certified_qty": "300"}
    ]
    with open("store_data/inventory/stock_dec.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=inventory_data[0].keys())
        writer.writeheader()
        writer.writerows(inventory_data)

    # 订单数据
    # CON_001: 需要 100个环保 ITM_101 (库存只有50) -> Turn 1 违约风险
    # CON_002: 需要 150个环保 ITM_105 (库存300) -> Turn 1 安全
    # CON_003: 需要 200个非环保 ITM_102 (库存1000) -> Turn 1 安全
    # CON_004: 需要 90个 ITM_104 (库存只有80) -> Turn 1 违约风险
    orders = {
        "CON_001": [{"item": "ITM_101", "qty": 100, "require_eco": True}],
        "CON_002": [{"item": "ITM_105", "qty": 150, "require_eco": True}],
        "CON_003": [{"item": "ITM_102", "qty": 200, "require_eco": False}],
        "CON_004": [{"item": "ITM_104", "qty": 90, "require_eco": False}]
    }
    with open("store_data/orders/vip_orders.json", "w") as f:
        json.dump(orders, f, indent=4)

    # 销售员记录 (隐秘关联 Turn 3 的伏笔)
    # EMP_A 负责 CON_001 (Turn 1 死)
    # EMP_B 负责 CON_002 (Turn 1 活，Turn 2 可能会死)
    # EMP_C 负责 CON_003 (Turn 1 活，Turn 2 可能会死)
    # EMP_D 负责 CON_004 (Turn 1 死)
    staff_data = [
        {"emp_id": "EMP_A", "name": "Carlos", "client_id": "CON_001", "key_sales": "Standard_Nails, Hammers"},
        {"emp_id": "EMP_B", "name": "Maria", "client_id": "CON_002", "key_sales": "Premium_Eco_Sealant, Brushes"}, # 伏笔：Premium_Eco_Sealant
        {"emp_id": "EMP_C", "name": "Luis", "client_id": "CON_003", "key_sales": "Basic_Wood, Titanium_Bolts"}, # 伏笔：Titanium_Bolts
        {"emp_id": "EMP_D", "name": "Ana", "client_id": "CON_004", "key_sales": "Steel_Wire"}
    ]
    with open("store_data/staff/sales_records.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=staff_data[0].keys())
        writer.writeheader()
        writer.writerows(staff_data)

def build_turn_2():
    os.makedirs("daily_updates", exist_ok=True)
    os.makedirs("action_plans", exist_ok=True)

    # 总部合规备忘录 (废除 ITM_105 的环保认证，导致 CON_002 违约，EMP_B 翻车)
    memo_content = """MEMORANDUM
URGENT: REGULATORY COMPLIANCE UPDATE
Effective immediately, all items classified under 'Low_VOC_Paint_Blue' (Item ID: ITM_105) 
have failed the revised state environmental inspection. 
Their eco-certified status is hereby revoked. Zero valid eco-stock remains for this item.
"""
    with open("daily_updates/compliance_memo.txt", "w") as f:
        f.write(memo_content)

    # 供应商延迟通知 (扣减 ITM_102 的可用库存 900件，导致只剩 100件。CON_003 需要 200件，导致 CON_003 违约，EMP_C 翻车)
    supplier_delays = [
        {"item_id": "ITM_102", "delayed_qty": "900", "reason": "Logistics Strike"}
    ]
    with open("daily_updates/supplier_delays.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["item_id", "delayed_qty", "reason"])
        writer.writeheader()
        writer.writerows(supplier_delays)

def build_turn_3():
    os.makedirs("appeals", exist_ok=True)

    # 员工申诉信
    appeals_content = """[EMP_B - Maria]: I worked so hard on the CON_002 account. The state regulation change is out of my control! Please reconsider.
[EMP_C - Luis]: The logistics strike ruined my delivery for CON_003. I've always brought in great margins for the store, it's not fair!
[EMP_A - Carlos]: Give me another chance.
"""
    with open("appeals/appeal_logs.txt", "w") as f:
        f.write(appeals_content)

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
