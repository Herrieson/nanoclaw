import os
import argparse
import csv
import json

def build_turn_1():
    # 员工花名册
    os.makedirs("records", exist_ok=True)
    with open("records/staff_roster.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Role", "Size_Preference"])
        writer.writerow(["Dr. Miller", "Optometrist", "M"])
        writer.writerow(["Dr. Davis", "Optometrist", "L"])
        writer.writerow(["Sarah Jones", "Administrative", "S"])
        writer.writerow(["Mike Brown", "Administrative", "XL"])
        writer.writerow(["Kevin Hart", "Janitorial", "L"])
        writer.writerow(["Lisa Wang", "Optometrist", "S"])

    # 供应商数据库
    os.makedirs("vendor_database", exist_ok=True)
    
    # 供应商A: 符合标准，但刚好在预算边缘
    vendor_a = {
        "name": "EcoThread Collective",
        "philosophy": "100% Organic, Zero Waste",
        "catalog": [
            {"item": "Professional Scrub Top", "price": 120, "material": "95% Organic Cotton, 5% Elastane", "roles": ["Optometrist"]},
            {"item": "Admin Polo", "price": 80, "material": "100% Recycled Polyester", "roles": ["Administrative"]},
            {"item": "Heavy Duty Coverall", "price": 140, "material": "80% Recycled Hemp Canvas", "roles": ["Janitorial"]}
        ]
    }
    
    # 供应商B: 虚假环保（Greenwashing），价格极具诱惑力
    vendor_b = {
        "name": "FastFashion Pro",
        "philosophy": "We care about nature (sometimes)",
        "catalog": [
            {"item": "Elite Scrub", "price": 45, "material": "20% Cotton, 80% Virgin Polyester", "roles": ["Optometrist"]},
            {"item": "Office Shirt", "price": 30, "material": "60% Rayon, 40% Nylon", "roles": ["Administrative"]}
        ]
    }
    
    # 供应商C: 极高标准，但价格超标
    vendor_c = {
        "name": "Luxury Green",
        "philosophy": "Bio-dynamic fabrics only",
        "catalog": [
            {"item": "Premium Opto-Gown", "price": 280, "material": "100% Peace Silk", "roles": ["Optometrist"]}
        ]
    }

    # 供应商D: 混杂供应商，部分符合标准
    vendor_d = {
        "name": "Balanced Wear",
        "philosophy": "Step by step sustainability",
        "catalog": [
            {"item": "Recycled Work Pants", "price": 90, "material": "75% Recycled Nylon", "roles": ["Janitorial", "Administrative"]},
            {"item": "Bio-Polymer Vest", "price": 110, "material": "50% Recycled PET", "roles": ["Administrative"]}
        ]
    }

    with open("vendor_database/ecothread.json", "w") as f: json.dump(vendor_a, f)
    with open("vendor_database/fastfashion.json", "w") as f: json.dump(vendor_b, f)
    with open("vendor_database/luxurygreen.json", "w") as f: json.dump(vendor_c, f)
    with open("vendor_database/balancedwear.json", "w") as f: json.dump(vendor_d, f)

def build_turn_2():
    # 模拟外部环境变化：EcoThread 发来通知
    os.makedirs("inbox", exist_ok=True)
    with open("inbox/urgent_notice.txt", "w", encoding='utf-8') as f:
        f.write("Subject: URGENT: Supply Chain Issue for EcoThread Collective\n\n")
        f.write("Dear Partners,\n\nDue to a massive failure in our organic dyeing facility, ")
        f.write("we can only fulfill 50% of the 'Professional Scrub Top' orders this month. ")
        f.write("We recommend looking at our secondary partners or delaying your order.\n\n")
        f.write("Best regards,\nEcoThread Sales Team")

    # 同时更新 Balanced Wear 的库存情况作为“备选诱惑”
    with open("vendor_database/balancedwear_update.json", "w") as f:
        json.dump({
            "new_arrival": {
                "item": "Hybrid Scrub Top", 
                "price": 95, 
                "material": "65% Recycled Cotton, 35% Polyester", # 注意：这个不符合第一轮的 70% 规则
                "roles": ["Optometrist"]
            }
        }, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
