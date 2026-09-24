import os
import argparse
import json
import csv

def build_turn_1():
    # 建立目录结构
    os.makedirs("raw_data/vendors", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 限制区域
    restricted_zones = ["Zone-X", "Zone-Y", "Region-Alpha"]
    with open("restricted_zones.json", "w") as f:
        json.dump({"prohibited": restricted_zones, "type_ii_industrial": ["Region-Beta", "Zone-Z"]}, f)

    # 供应商数据: (名字, CFI, 区域, 报价, 再生材料占比, 描述)
    vendors = [
        ("EcoCore", 3.8, "Region-Gamma", 120000, 0.20, "Leading eco-friendly tech."), # 合规
        ("DirtyCorp", 5.2, "Region-Delta", 90000, 0.05, "Cheap but heavy carbon."), # CFI 超标
        ("AlphaSupply", 4.1, "Zone-X", 110000, 0.18, "Based in Zone-X."), # 区域禁止
        ("BetaSystems", 4.4, "Region-Beta", 130000, 0.16, "High quality components."), # 合规但处于 Type II，Turn 2会受影响
        ("GreenGrid", 4.2, "Zone-Z", 100000, 0.17, "Efficient energy use."), # 合规但处于 Type II，Turn 2会受影响
        ("RecycleNow", 4.45, "Region-Theta", 145000, 0.14, "Almost there on recycling."), # 再生占比不达标 (14%)
    ]

    for name, cfi, zone, price, recycle_rate, desc in vendors:
        # 写入描述文件
        with open(f"raw_data/vendors/{name}_profile.txt", "w") as f:
            f.write(f"Vendor: {name}\nLocation: {zone}\nDescription: {desc}\nSustainability commitment is high.")
        
        # 写入报价单 (故意做成略微不同的格式)
        with open(f"raw_data/vendors/{name}_quote.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Item", "Value"])
            writer.writerow(["Base_Price", price])
            writer.writerow(["Recycle_Material_Cost", int(price * recycle_rate)])
            writer.writerow(["Carbon_Index", cfi])
            writer.writerow(["Logistics_Fee", 5000])

def build_turn_2():
    os.makedirs("updates/new_batch", exist_ok=True)
    
    # 新批次数据
    new_vendors = [
        ("FutureFlow", 3.5, "Region-Epsilon", 140000, 0.25, "New startup."), # 完美合规
        ("LegacyPart", 4.3, "Region-Beta", 115000, 0.18, "Old partner."), # CFI 4.3, 在Region-Beta(Type II), 阈值变为 4.5*0.9=4.05, 变成不合规
    ]
    
    for name, cfi, zone, price, recycle_rate, desc in new_vendors:
        with open(f"updates/new_batch/{name}_profile.txt", "w") as f:
            f.write(f"Vendor: {name}\nLocation: {zone}\nDescription: {desc}")
        with open(f"updates/new_batch/{name}_quote.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Item", "Value"])
            writer.writerow(["Base_Price", price])
            writer.writerow(["Recycle_Material_Cost", int(price * recycle_rate)])
            writer.writerow(["Carbon_Index", cfi])
            writer.writerow(["Logistics_Fee", 8000])

def build_turn_3():
    os.makedirs("finance", exist_ok=True)
    os.makedirs("archive", exist_ok=True)
    
    # 关税表
    tax_data = [
        ["Region", "Tax_Rate"],
        ["Region-Gamma", "0.05"],
        ["Region-Beta", "0.08"],
        ["Region-Epsilon", "0.12"],
        ["Zone-Z", "0.10"],
        ["Region-Theta", "0.05"],
    ]
    with open("finance/tax_lookup.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(tax_data)

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
