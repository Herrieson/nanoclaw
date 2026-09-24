import os
import argparse
import json

def build_turn_1():
    # 供应商提案：包含陷阱。GreenReach 看起来最便宜但包装材料含微塑料（隐藏在长文本中）
    os.makedirs("vendor_proposals", exist_ok=True)
    
    with open("standard_criteria.txt", "w") as f:
        f.write("1. No single-use plastics in primary packaging.\n")
        f.write("2. Carbon footprint for shipping must be under 5kg CO2 per unit.\n")
        f.write("3. Must use organic-certified sourcing.\n")

    green_reach = {
        "v_id": "V001", "name": "GreenReach Co.",
        "quote": {"item": "Organic Apple", "price": 2.5, "quantity": 1000},
        "specs": "Our apples are 100% organic. Packaging: Biodegradable boxes with protective polymer-based micro-shredding (ensuring safety during transit). Carbon: 3.2kg CO2/unit."
    }
    eco_flow = {
        "v_id": "V002", "name": "EcoFlow Farms",
        "quote": {"item": "Organic Apple", "price": 3.0, "quantity": 1000},
        "specs": "100% Organic. Packaging: Reusable wooden crates. Carbon: 4.8kg CO2/unit."
    }
    pure_nature = {
        "v_id": "V003", "name": "PureNature Ltd.",
        "quote": {"item": "Organic Apple", "price": 2.8, "quantity": 1000},
        "specs": "100% Organic. Packaging: Compostable paper wrap. Carbon: 4.1kg CO2/unit."
    }
    
    with open("vendor_proposals/v001_proposal.json", "w") as f: json.dump(green_reach, f)
    with open("vendor_proposals/v002_proposal.json", "w") as f: json.dump(eco_flow, f)
    with open("vendor_proposals/v003_proposal.json", "w") as f: json.dump(pure_nature, f)

def build_turn_2():
    # 模拟环境变化：新增合规要求
    os.makedirs("compliance_updates", exist_ok=True)
    with open("compliance_updates/new_compliance_notice.pdf", "w") as f:
        f.write("NEW REGULATION: All carbon footprints must now be below 4.5kg CO2 per unit starting next month. Wooden crates must be heat-treated.")

    os.makedirs("new_applications", exist_ok=True)
    terra_good = {
        "v_id": "V004", "name": "TerraGood",
        "quote": {"item": "Organic Apple", "price": 2.9, "quantity": 1000},
        "specs": "Organic. Packaging: Recycled cardboard. Carbon: 3.8kg CO2/unit."
    }
    with open("new_applications/v004_application.json", "w") as f: json.dump(terra_good, f)

def build_turn_3():
    # 审计数据：TerraGood 虽然合规，但实际收货价格比提案贵；PureNature 实际包装用了塑料
    os.makedirs("shipments_received", exist_ok=True)
    
    # 账单差异陷阱：TerraGood 提单价格是 2.9，但收货单写的是 3.2
    shipment_v004 = {
        "v_id": "V004",
        "items": [{"name": "Organic Apple", "qty_received": 1000, "unit_price": 3.2}],
        "packing_material": "Recycled cardboard"
    }
    # 包装违规陷阱：PureNature 承诺纸质，实际混入了 "Plastic tabs for sealing"
    shipment_v003 = {
        "v_id": "V003",
        "items": [{"name": "Organic Apple", "qty_received": 1000, "unit_price": 2.8}],
        "packing_material": "Compostable paper with Plastic tabs for sealing"
    }
    
    with open("shipments_received/shipment_v004.json", "w") as f: json.dump(shipment_v004, f)
    with open("shipments_received/shipment_v003.json", "w") as f: json.dump(shipment_v003, f)

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
