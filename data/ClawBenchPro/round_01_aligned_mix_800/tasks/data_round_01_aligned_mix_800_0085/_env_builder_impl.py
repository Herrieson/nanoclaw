import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟餐厅复杂的原材料供应目录和供应商报价
    os.makedirs("supply_chain/vendors", exist_ok=True)
    os.makedirs("supply_chain/specifications", exist_ok=True)
    
    # 供应商 A：价格极低，但碳排放高 (陷阱)
    vendor_a = [
        {"item": "Organic Chicken", "price_per_kg": 12.5, "carbon_footprint_g": 4500, "distance_km": 1200},
        {"item": "Wild Salmon", "price_per_kg": 28.0, "carbon_footprint_g": 8000, "distance_km": 3500},
        {"item": "Avocado", "price_per_kg": 4.5, "carbon_footprint_g": 1200, "distance_km": 2000}
    ]
    # 供应商 B：价格中等，本地供应，碳排放低
    vendor_b = [
        {"item": "Organic Chicken", "price_per_kg": 15.0, "carbon_footprint_g": 1800, "distance_km": 150},
        {"item": "Wild Salmon", "price_per_kg": 35.0, "carbon_footprint_g": 2200, "distance_km": 400},
        {"item": "Avocado", "price_per_kg": 8.0, "carbon_footprint_g": 500, "distance_km": 100}
    ]
    
    with open("supply_chain/vendors/global_mega_corp.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=vendor_a[0].keys())
        writer.writeheader()
        writer.writerows(vendor_a)
        
    with open("supply_chain/vendors/local_green_farms.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=vendor_b[0].keys())
        writer.writeheader()
        writer.writerows(vendor_b)

    # 复杂的评分逻辑文档
    with open("supply_chain/specifications/scoring_v1.txt", "w") as f:
        f.write("Scoring Logic Policy:\n")
        f.write("1. Total Score = (100 / Price_Per_Kg) * 0.4 + (5000 / Carbon_Footprint_G) * 0.6\n")
        f.write("2. If Distance_KM > 1000, deduct 15 points from total score.\n")
        f.write("3. Sustainability threshold: Any item with Carbon_Footprint_G > 5000 is FLAG_RED.\n")

def build_turn_2():
    # 注入突发情况：环保法规更新文件
    os.makedirs("regulatory_updates", exist_ok=True)
    with open("regulatory_updates/new_green_tax.json", "w") as f:
        json.dump({
            "effective_date": "2024-06-01",
            "carbon_tax_rate": 0.05, # 每克碳排放额外征收的费用
            "penalty_threshold_g": 3000, # 超过此值的排放量征收双倍税率
            "local_bonus_km": 200 # 距离小于此值的免除50%运输税
        }, f)

def build_turn_3():
    # 模拟供应商信用破产，导致部分历史选择失效
    os.makedirs("incidents", exist_ok=True)
    with open("incidents/vendor_blacklist.log", "w") as f:
        f.write("TIMESTAMP: 2024-05-20\n")
        f.write("REPORT: 'local_green_farms' has been found violating waste disposal laws.\n")
        f.write("ACTION: Suspended all contracts pending investigation.\n")

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
