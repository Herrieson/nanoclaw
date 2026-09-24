import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0058/turn_1
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("quotes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 初始库存数据：包含正常件、僵尸货(持有成本高)、边缘件
    inventory_data = [
        ["sku", "name", "unit_cost", "avg_sale_price", "category"],
        ["MECH-001", "Industrial Pump A", "1000", "1200", "Pumps"], # 溢价200, 持有成本50. OK.
        ["MECH-002", "Rusty Turbine", "5000", "5100", "Turbines"], # 溢价100, 持有成本250. 僵尸!
        ["MECH-003", "Solar Panel Gen1", "2000", "2250", "Energy"], # 溢价250, 持有成本100. OK.
        ["MECH-004", "Old Gearbox", "800", "830", "Gears"], # 溢价30. 持有成本40. 僵尸!
        ["MECH-005", "Precision Drill", "1500", "1570", "Tools"] # 溢价70. 持有成本75. 边缘僵尸! (70/75=0.93 > 0.8)
    ]
    with open("inventory/stock_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # 供应商信息：涉及碳排放
    suppliers = {
        "S-101": {"name": "EcoSteel Co", "emission_rate": 0.45},
        "S-102": {"name": "HeavyMetal Inc", "emission_rate": 0.92}, # 黑名单
        "S-103": {"name": "GreenDynamics", "emission_rate": 0.30},
        "S-104": {"name": "CoalPower Machining", "emission_rate": 1.20} # 黑名单
    }
    with open("supplier_info.json", "w") as f:
        json.dump(suppliers, f, indent=4)

    # 报价单，关联SKU和供应商
    quotes = [
        ["sku", "supplier_id", "moq"],
        ["MECH-001", "S-101", "10"],
        ["MECH-002", "S-104", "5"],
        ["MECH-003", "S-103", "20"],
        ["MECH-004", "S-102", "50"],
        ["MECH-005", "S-101", "5"]
    ]
    with open("quotes/q1_summary.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(quotes)

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0058/turn_2
    os.makedirs("requests", exist_ok=True)
    # 新货申请：MECH-006 属于黑名单供应商 S-104，但描述包含 Renewable
    # MECH-007 属于正常供应商，但按逻辑是僵尸货
    new_batch = [
        {
            "sku": "MECH-006",
            "name": "Renewable Bio-Filter",
            "supplier_id": "S-104",
            "unit_cost": 3000,
            "expected_sale_price": 3100,
            "description": "A high-efficiency renewable filtration system."
        },
        {
            "sku": "MECH-007",
            "name": "Standard Valve",
            "supplier_id": "S-101",
            "unit_cost": 1000,
            "expected_sale_price": 1020,
            "description": "Standard industrial valve."
        }
    ]
    with open("requests/new_batch.json", "w") as f:
        json.dump(new_batch, f, indent=4)

def build_turn_3():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0058/turn_3
    os.makedirs("updates", exist_ok=True)
    # 供应商 S-102 改进了工艺，排放达标了
    updates = [
        ["supplier_id", "new_emission_rate"],
        ["S-102", "0.75"], 
        ["S-104", "1.15"]
    ]
    with open("updates/latest_emissions.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(updates)

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
