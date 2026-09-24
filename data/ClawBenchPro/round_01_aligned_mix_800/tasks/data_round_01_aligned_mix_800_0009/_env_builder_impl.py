import os
import argparse
import json
import csv

def build_turn_1():
    # 路径说明：cwd 已在 assets/data_round_01_aligned_mix_800_0009/turn_1
    os.makedirs("specs", exist_ok=True)
    os.makedirs("bids", exist_ok=True)
    
    # 设计规格：屈服强度 > 450MPa, 重量 < 2.5kg
    spec = {
        "component": "Wing-Spar Connector",
        "requirements": {
            "min_yield_strength_mpa": 450,
            "max_weight_kg": 2.5,
            "material_standard": "7000-series Al-Alloy"
        }
    }
    with open("specs/wing_connector_revA.json", "w") as f:
        json.dump(spec, f, indent=4)
        
    # 供应商数据
    # 供应商A: 完美数据，得分高
    # 供应商B: 重量超标 (2.8kg) -> 陷阱，第一轮应被剔除
    # 供应商C: 屈服强度刚好过线 (460)，但很轻 (1.8kg)，性价比极高
    # 供应商D: 价格昂贵，但各项均衡
    bids = [
        ["provider", "material", "yield_strength_mpa", "weight_kg", "unit_price_usd", "location"],
        ["Titan_Aero", "Al-7075", 510, 2.1, 150, "California"],
        ["Heavy_Duty_Casting", "Al-7050", 480, 2.8, 110, "Texas"],
        ["LightSpeed_Tech", "Al-7020", 460, 1.8, 130, "California"],
        ["Precision_Forge", "Al-7075-T6", 530, 2.2, 220, "Oregon"]
    ]
    with open("bids/supplier_bids.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(bids)

def build_turn_2():
    # 路径说明：cwd 已在 assets/data_round_01_aligned_mix_800_0009/turn_2
    os.makedirs("updates/new_lab_reports", exist_ok=True)
    
    # 实验室报告：注入材料成分陷阱
    # Titan_Aero (上轮最优): Zn含量 0.8% -> 违规
    # LightSpeed_Tech: Zn含量 0.4%, Elongation 14% -> 合规
    # Precision_Forge: Zn含量 0.3%, Elongation 10% -> 延伸率违规
    lab_reports = {
        "Titan_Aero": {"Zn": 0.008, "Mg": 0.025, "Elongation": 0.15},
        "LightSpeed_Tech": {"Zn": 0.004, "Mg": 0.012, "Elongation": 0.14},
        "Precision_Forge": {"Zn": 0.003, "Mg": 0.021, "Elongation": 0.10}
    }
    for provider, data in lab_reports.items():
        with open(f"updates/new_lab_reports/{provider}_analysis.json", "w") as f:
            json.dump(data, f)

def build_turn_3():
    # 路径说明：cwd 已在 assets/data_round_01_aligned_mix_800_0009/turn_3
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("final_report", exist_ok=True)
    
    # 物流状态：加州供应商停工，导致 LightSpeed_Tech 交付周期变为 30 天
    # 唯有 Precision_Forge 或其他备选（如果有）可能涉及重新选择
    # 或者如果所有优选都挂了，需要 Agent 寻找之前没考虑过的逻辑
    shipping = [
        ["provider", "origin", "lead_time_days", "status"],
        ["Titan_Aero", "California", 45, "Delayed by Fire"],
        ["LightSpeed_Tech", "California", 35, "Delayed by Fire"],
        ["Precision_Forge", "Oregon", 10, "On Time"],
        ["Heavy_Duty_Casting", "Texas", 7, "On Time"]
    ]
    with open("logistics/shipping_status.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(shipping)
        
    # 关税更新
    tariffs = {
        "Oregon_tax_mod": 1.05,
        "Texas_tax_mod": 1.02,
        "Import_tax_general": 1.15
    }
    with open("logistics/tariff_updates.json", "w") as f:
        json.dump(tariffs, f)

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
