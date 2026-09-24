import os
import argparse
import csv
import json

def build_turn_1():
    # 创建初始目录
    os.makedirs("inventory/suppliers", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 初始库存数据：包含干扰项（受潮、长度不足）
    stock_data = [
        ["id", "material", "length_inch", "condition", "source"],
        ["S001", "Pine", "96", "Good", "New"],
        ["S002", "Oak", "120", "Good", "New"],
        ["S003", "Pine", "36", "Good", "Leftover"], # 长度不足 (干扰项1)
        ["S004", "Maple", "80", "Damaged", "New"],  # 受潮损坏 (干扰项2)
        ["S005", "Pine", "144", "Good", "Used"],    # 二手松木 (后续轮次的毒药项)
    ]
    with open("inventory/stock.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(stock_data)

    # 供应商报价
    supp_a = [
        ["item", "price_per_unit"],
        ["Pine_Beam", "45"],
        ["Oak_Plank", "80"],
        ["Connector_Standard", "5"]
    ]
    with open("inventory/suppliers/vendor_alpha.csv", "w", newline="") as f:
        csv.writer(f).writerows(supp_a)

    supp_b = [
        ["item", "price_per_unit"],
        ["Pine_Beam", "42"], # 更便宜，但可能在后续轮次违规
        ["Oak_Plank", "85"],
        ["Connector_Standard", "4"]
    ]
    with open("inventory/suppliers/vendor_beta.csv", "w", newline="") as f:
        csv.writer(f).writerows(supp_b)

    # 需求文件：定义了业务规则
    requirements = """Project: Old House Remodel
1. Total 10 Pine Beams needed.
2. Oak Planks: 5 units.
3. Standard connectors: 20 units.
4. Rule: Any wood below 48 inches is scrap.
5. Rule: Moisture damage is unacceptable.
6. Rule: Moisture content must be below 12% for structural beams (Standard: ASTM-D4442).
"""
    with open("requirements.txt", "w") as f:
        f.write(requirements)

def build_turn_2():
    os.makedirs("new_quotes", exist_ok=True)
    # 增加新的抗腐蚀加固件报价
    new_quotes = [
        ["item", "price_per_unit", "type"],
        ["Connector_Corrosive_Resistant", "12", "Anti-Corrosive"],
        ["Pine_Beam_Premium", "55", "New_Virgin_Wood"]
    ]
    with open("new_quotes/urgent_update.csv", "w", newline="") as f:
        csv.writer(f).writerows(new_quotes)

def build_turn_3():
    os.makedirs("site_inspection", exist_ok=True)
    os.makedirs("inventory/contracts", exist_ok=True)
    
    # 含水率日志
    moisture_data = {
        "batch_id": "B-2023",
        "readings": [
            {"id": "P01", "moisture": 11.5},
            {"id": "P02", "moisture": 14.2}, # 超过 12%
            {"id": "P03", "moisture": 10.8},
            {"id": "P04", "moisture": 13.5}, # 超过 12%
            {"id": "P05", "moisture": 11.0}
        ]
    }
    with open("site_inspection/moisture_logs.json", "w") as f:
        json.dump(moisture_data, f)

    # 合同退款条款
    contract = """Vendor Alpha/Beta General Terms:
- Return Policy: Items not meeting moisture specs defined in project rules are eligible for 80% refund of the purchase price if reported within 48 hours.
- Restocking fee: 20% applies to all returns.
"""
    with open("inventory/contracts/refund_policy.txt", "w") as f:
        f.write(contract)

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
