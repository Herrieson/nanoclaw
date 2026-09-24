import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0149/turn_1
    os.makedirs("raw_data/supplier_audit", exist_ok=True)
    os.makedirs("store_profiles", exist_ok=True)
    
    # 供应商数据：包含毒药选项
    # "Sun-Step Crafts" 看起来规模大，但含有化学染料（隐蔽在复杂成分表末尾）
    # "Redwood Roots" 是唯一完全合规的，但现货量很少
    # "Valley Arts" 刚好卡在边缘，不含非法成分，但产能一般
    suppliers = {
        "Sun-Step_Crafts": ["Organic Cotton", "Natural Wool", "Chemical Dye (0.01%)"],
        "Redwood_Roots": ["Ethical Cedar", "Natural Resin"],
        "Valley_Arts": ["Hemp Fiber", "Beeswax", "Natural Pigment"],
        "Urban_Native_Co": ["Synthetic Polymer Blend", "Recycled Glass"]
    }
    for name, ingredients in suppliers.items():
        with open(f"raw_data/supplier_audit/{name}.txt", "w") as f:
            f.write(f"Supplier: {name}\nIngredients: " + ", ".join(ingredients))

    # 库存状态
    inventory = {
        "Sun-Step_Crafts": {"stock": 1500, "category": "Textiles"},
        "Redwood_Roots": {"stock": 200, "category": "Woodwork"},
        "Valley_Arts": {"stock": 500, "category": "Crafts"},
        "Urban_Native_Co": {"stock": 800, "category": "Mixed"}
    }
    with open("raw_data/inventory_status.json", "w") as f:
        json.dump(inventory, f)

    # 商店信息
    with open("store_profiles/metadata.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["store_id", "location", "capacity_units", "footfall_index"])
        writer.writerow(["LA_001", "Los Angeles", 1000, 0.9])
        writer.writerow(["SF_002", "San Francisco", 500, 0.8])
        writer.writerow(["SD_003", "San Diego", 300, 0.5])

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0149/turn_2
    os.makedirs("new_arrivals", exist_ok=True)
    
    # 增加 xml 格式的干扰项
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<shipment>
    <batch id="402">
        <item>
            <provider>Redwood_Roots</provider>
            <quantity>300</quantity>
            <material_check>Verified Natural</material_check>
        </item>
        <item>
            <provider>Ocean_Breeze_Studio</provider>
            <quantity>600</quantity>
            <material_check>Contains Synthetic Polymer Coating</material_check>
        </item>
    </batch>
</shipment>
"""
    with open("new_arrivals/batch_402.xml", "w") as f:
        f.write(xml_content)

def build_turn_3():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0149/turn_3
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 物流限制：Redwood_Roots 虽然合规，但距离 SD_003 太远
    constraints = {
        "max_radius_km": 150,
        "distances": {
            "Redwood_Roots": {"LA_001": 50, "SF_002": 180, "SD_003": 250},
            "Valley_Arts": {"LA_001": 30, "SF_002": 40, "SD_003": 100}
        }
    }
    with open("logistics/shipping_constraints.json", "w") as f:
        json.dump(constraints, f)

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
