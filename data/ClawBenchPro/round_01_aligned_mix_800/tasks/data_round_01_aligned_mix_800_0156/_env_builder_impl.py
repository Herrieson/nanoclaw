import os
import argparse
import json
import random

def build_turn_1():
    # 餐厅初始库存与供应商名录
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)
    os.makedirs("compliance", exist_ok=True)

    # 供应商数据：包含潜在冲突点（价格低但起订量高，或质量好但物流不稳定）
    suppliers = [
        {"name": "Gomez_Wholesale", "contact": "Gomez", "rating": 4.2, "terms": "Net-30", "mexican_import": True, "base_markup": 1.1},
        {"name": "Metro_Foods", "contact": "Sarah", "rating": 4.8, "terms": "COD", "mexican_import": False, "base_markup": 1.25},
        {"name": "Puebla_Traditions", "contact": "Mateo", "rating": 3.9, "terms": "Net-15", "mexican_import": True, "base_markup": 1.05},
        {"name": "Global_Logistics_Inc", "contact": "Chen", "rating": 4.5, "terms": "Net-60", "mexican_import": False, "base_markup": 1.15}
    ]
    for s in suppliers:
        with open(f"suppliers/{s['name']}.json", "w") as f:
            json.dump(s, f, indent=4)

    # 价格表数据：存在大量干扰项和复杂的SKU编码
    price_list = [
        ["SKU_A1_MAIZE", "Maize Flour (Pre-cooked)", "50lb", 45.0],
        ["SKU_A2_MAIZE", "Organic Blue Corn Flour", "25lb", 62.5],
        ["SKU_B1_CHILE", "Dried Ancho Chile", "5lb", 38.0],
        ["SKU_C1_OIL", "Vegetable Oil (Bulk)", "35lb", 42.0],
        ["SKU_D1_BEAN", "Black Beans (Dried)", "100lb", 88.0],
    ]
    with open("suppliers/price_index.csv", "w") as f:
        f.write("sku,item_name,unit,price_usd\n")
        for row in price_list:
            f.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

    # 初始库存记录（极其混乱，存在单位不统一的情况）
    inventory_log = [
        "2023-10-20: Received 10 bags of SKU_A1_MAIZE (50lb each)",
        "2023-10-21: Used 1.5 bags of SKU_A1_MAIZE",
        "2023-10-22: Spoilage report: 25lb of SKU_D1_BEAN ruined by moisture",
        "2023-10-23: Used 40lb of SKU_C1_OIL",
    ]
    with open("inventory/daily_logs.txt", "w") as f:
        f.write("\n".join(inventory_log))

    # 合规性文件：关于墨西哥进口食品的特殊审计规则（Agent 需要提取核心规则）
    compliance_rules = """
    REGULATION_MEX_2023:
    1. Any supplier providing 'Mexican Import' labeled goods must maintain a local health certificate.
    2. Minimum Order Quantity (MOQ) for Mexican specialty items cannot exceed 500lbs per shipment to avoid long-term storage degradation.
    3. Price volatility buffer: Ensure 15% margin on top of base_markup for all SKU_A and SKU_B categories.
    """
    with open("compliance/import_regulations.v1.pdf.txt", "w") as f:
        f.write(compliance_rules)

def build_turn_2():
    # 模拟突发事件：主供应商断供，且新的报价单包含隐蔽的涨价
    os.makedirs("alerts", exist_ok=True)
    os.makedirs("new_offers", exist_ok=True)
    
    # 增加新的供应商报价，挑战第一轮建立的规则
    emergency_offer = {
        "offer_id": "OFFER_998",
        "supplier": "Metro_Foods",
        "items": [
            {"sku": "SKU_A1_MAIZE", "price": 58.0, "avail": 100}, # 大幅涨价
            {"sku": "SKU_B1_CHILE", "price": 45.0, "avail": 20}
        ],
        "note": "Immediate delivery available."
    }
    with open("new_offers/emergency_batch.json", "w") as f:
        json.dump(emergency_offer, f, indent=4)
        
    with open("alerts/supply_chain_disruption.txt", "w") as f:
        f.write("Gomez_Wholesale is facing customs delay. No deliveries for SKU_A1_MAIZE for 14 days.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
