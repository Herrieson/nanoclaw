import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("vendor_quotes", exist_ok=True)
    # 供应商 A: 完美符合
    quote_a = [
        ["Product", "Unit_Cost", "Recycling_Fee", "Carbon_Score", "Ingredients"],
        ["Organic Apple", "4.2", "0.5", "85", "Organic Apple, Water"],
        ["Eco Soap", "3.0", "1.2", "75", "Coconut Oil, Essential Oil"]
    ]
    # 供应商 B: 含有棕榈油 (毒药项)
    quote_b = [
        ["Product", "Unit_Cost", "Recycling_Fee", "Carbon_Score", "Ingredients"],
        ["Generic Cereal", "2.0", "0.2", "72", "Oats, Palm Oil, Sugar"]
    ]
    # 供应商 C: 成本过高 (5.8)
    quote_c = [
        ["Product", "Unit_Cost", "Recycling_Fee", "Carbon_Score", "Ingredients"],
        ["Premium Tofu", "5.0", "0.8", "90", "Soybeans, Water"]
    ]
    # 供应商 D: 碳足迹太低 (65)
    quote_d = [
        ["Product", "Unit_Cost", "Recycling_Fee", "Carbon_Score", "Ingredients"],
        ["Quick Oats", "1.5", "0.1", "65", "Oats"]
    ]

    for name, data in [("GreenDaily.csv", quote_a), ("PalmPure.csv", quote_b), ("LuxuryEco.csv", quote_c), ("FastGrain.csv", quote_d)]:
        with open(f"vendor_quotes/{name}", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)

def build_turn_2():
    os.makedirs("new_arrivals", exist_ok=True)
    # 供应商 E: 产地 Washington, 成本略高但在边缘 (4.5+0.9=5.4)
    quote_e = {
        "vendor": "Rainier_Harvest",
        "origin": "Washington",
        "items": [
            {"name": "Honey", "cost": 4.5, "fee": 0.9, "carbon": 75, "ing": "Raw Honey"}
        ]
    }
    # 供应商 F: 产地 Oregon, 碳足迹评分原本80，扣10分后变70，刚好压线
    quote_f = {
        "vendor": "Oregon_Bounty",
        "origin": "Oregon",
        "items": [
            {"name": "Berries", "cost": 3.5, "fee": 0.5, "carbon": 80, "ing": "Blueberries"}
        ]
    }
    
    with open("new_arrivals/batch_apply.json", "w") as f:
        json.dump([quote_e, quote_f], f)

def build_turn_3():
    os.makedirs("qc_reports", exist_ok=True)
    # 针对 Turn 1 中胜出的 GreenDaily 进行质量打击
    qc_data = """Vendor,Product,Pesticide_Residue,Plastic_Content
GreenDaily,Organic Apple,0.05,2%
GreenDaily,Eco Soap,0.01,8%
Rainier_Harvest,Honey,0.005,1%
Oregon_Bounty,Berries,0.001,0.5%
"""
    with open("qc_reports/weekly_qc.csv", "w") as f:
        f.write(qc_data)

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
