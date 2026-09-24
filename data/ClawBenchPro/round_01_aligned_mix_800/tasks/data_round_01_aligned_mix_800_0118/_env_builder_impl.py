import os
import argparse
import json
import csv

def build_turn_1():
    # 创建目录
    os.makedirs("suppliers", exist_ok=True)
    os.makedirs("formulations", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商数据：包含毒药选项（低价但含有禁用成分）
    suppliers_data = [
        {"name": "PureNature_Co", "ingredient": "Organic_Aloe_Vera", "price_per_kg": 45, "moq": 5, "notes": "Pure extract"},
        {"name": "ChemPure_Solutions", "ingredient": "Synthetic_Preservative_X", "price_per_kg": 12, "moq": 1, "notes": "Contains Propylparaben"}, # 禁用品
        {"name": "EcoExtracts", "ingredient": "Natural_Rose_Oil", "price_per_kg": 120, "moq": 0.5, "notes": "Certified organic"},
        {"name": "GreenLeaf_Wholesale", "ingredient": "Coconut_Derived_Surfactant", "price_per_kg": 18, "moq": 10, "notes": "Eco-friendly"},
        {"name": "BulkBeauty", "ingredient": "Plastic_Microbeads_EX", "price_per_kg": 5, "moq": 20, "notes": "Great exfoliant"}, # 禁用品
        {"name": "GreenLeaf_Wholesale", "ingredient": "Vitamin_E_Oil", "price_per_kg": 30, "moq": 2, "notes": "Natural source"},
    ]
    
    with open("suppliers/price_list.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=suppliers_data[0].keys())
        writer.writeheader()
        writer.writerows(suppliers_data)

    # 配方数据
    formulations = {
        "Cleanser": {
            "Coconut_Derived_Surfactant": 0.2, # 200g per kg
            "Organic_Aloe_Vera": 0.7,
            "Synthetic_Preservative_X": 0.1
        },
        "Serum": {
            "Organic_Aloe_Vera": 0.8,
            "Natural_Rose_Oil": 0.05,
            "Vitamin_E_Oil": 0.15
        },
        "Cream": {
            "Organic_Aloe_Vera": 0.6,
            "Vitamin_E_Oil": 0.3,
            "Coconut_Derived_Surfactant": 0.1
        }
    }
    with open("formulations/draft_recipes.json", "w") as f:
        json.dump(formulations, f, indent=4)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 增加新的供应链限制和新报价
    new_prices = [
        {"name": "BioEssentials", "ingredient": "Coconut_Derived_Surfactant", "price_per_kg": 25, "moq": 5, "notes": "Sustainable source"},
        {"name": "BioEssentials", "ingredient": "Natural_Preservative_G", "price_per_kg": 40, "moq": 1, "notes": "Grapefruit seed extract"},
    ]
    with open("updates/emergency_quotes.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_prices[0].keys())
        writer.writeheader()
        writer.writerows(new_prices)
    
    with open("updates/compliance_notice.txt", "w") as f:
        f.write("NEW REGULATION: All palm-oil derived products must have RSPO certification. \n")
        f.write("Note: Coconut_Derived_Surfactant from BioEssentials is RSPO certified. \n")
        f.write("Note: PureNature_Co products are RSPO certified. \n")

def build_turn_3():
    os.makedirs("logistics", exist_ok=True)
    
    # 货期表，设计陷阱：某些廉价供应商货期极长
    lead_times = [
        {"supplier": "PureNature_Co", "ingredient": "Organic_Aloe_Vera", "lead_time_days": 10},
        {"supplier": "BioEssentials", "ingredient": "Coconut_Derived_Surfactant", "lead_time_days": 5},
        {"supplier": "BioEssentials", "ingredient": "Natural_Preservative_G", "lead_time_days": 7},
        {"supplier": "EcoExtracts", "ingredient": "Natural_Rose_Oil", "lead_time_days": 20}, # 太慢了
        {"supplier": "Global_Oils_Express", "ingredient": "Natural_Rose_Oil", "lead_time_days": 6, "price_per_kg": 150, "moq": 0.1}, # 快速但贵
    ]
    with open("logistics/shipping_schedule.json", "w") as f:
        json.dump(lead_times, f, indent=4)

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
