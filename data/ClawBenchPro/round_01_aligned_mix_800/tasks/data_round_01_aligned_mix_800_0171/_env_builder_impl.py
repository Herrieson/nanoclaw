import os
import argparse
import csv
import json

def build_turn_1():
    # Base directory assumed to be assets/data_round_01_aligned_mix_800_0171/turn_1
    os.makedirs("manifests", exist_ok=True)
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # orders.csv
    orders = [
        ["order_id", "category", "weight_kg", "revenue", "destination"],
        ["ORD001", "Medical Supplies", "500", "5000", "London"],
        ["ORD002", "Electronics", "1200", "8000", "Tokyo"],
        ["ORD003", "Furniture", "3000", "4500", "Berlin"],
        ["ORD004", "Medical Supplies", "200", "3000", "Paris"],
        ["ORD005", "Consumer Goods", "1500", "3500", "New York"]
    ]
    with open("manifests/pending_orders.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(orders)

    # port_status.json
    ports = {
        "Port_Alpha": {"base_cost_per_kg": 1.2, "lead_time_days": 3, "capacity_kg": 2000},
        "Port_Beta": {"base_cost_per_kg": 0.8, "lead_time_days": 7, "capacity_kg": 5000},
        "Port_Gamma": {"base_cost_per_kg": 2.5, "lead_time_days": 1, "capacity_kg": 1000}
    }
    with open("logistics/port_status.json", "w") as f:
        json.dump(ports, f, indent=4)

    # trusted_partners.txt
    with open("vendors/trusted_partners.txt", "w") as f:
        f.write("GlobalLogix\nSwiftCargo\nOceanBridge")

    # pricing_policy.md
    pricing_policy = """
# 供应商阶梯计价政策
1. **GlobalLogix**: 基础运费 + 5% 管理费。若货物重量 > 1000kg，超出部分管理费降至 2%。
2. **SwiftCargo**: 固定加价 $200 + 基础运费。
3. **OceanBridge**: 仅限 > 2000kg 的货物，基础运费打 9 折，但额外收取 $500 报关费。
    """
    with open("vendors/pricing_policy.md", "w") as f:
        f.write(pricing_policy)

def build_turn_2():
    # Assumes environment from turn_1 is copied
    os.makedirs("manifests", exist_ok=True)
    
    # New arrivals with a "trap": Order 007 looks profitable but Fragile requirement will kill margin
    new_orders = [
        ["order_id", "category", "weight_kg", "revenue", "destination", "tags"],
        ["ORD006", "Electronics", "800", "6000", "Singapore", "Standard"],
        ["ORD007", "Luxury Goods", "100", "2000", "Dubai", "Fragile"],
        ["ORD008", "Medical Supplies", "600", "7000", "London", "Standard"]
    ]
    with open("manifests/new_arrivals.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_orders)
    
    # Update policy - hidden in turn_2's logic
    # Note: Fragile insurance is $300 flat. Electronics tax +10% of base_cost.

def build_turn_3():
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("emergency", exist_ok=True)
    
    # XML format for variety
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<report>
    <port name="Port_Alpha">
        <status>Congested</status>
        <max_daily_inbound_kg>800</max_daily_inbound_kg>
    </port>
    <port name="Port_Beta">
        <status>Normal</status>
        <max_daily_inbound_kg>4000</max_daily_inbound_kg>
    </port>
</report>
"""
    with open("logistics/congestion_report.xml", "w") as f:
        f.write(xml_content)
    
    # Scenario: GlobalLogix (the primary partner for heavy stuff) goes offline
    with open("vendors/trusted_partners.txt", "w") as f:
        f.write("SwiftCargo\nOceanBridge")

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
