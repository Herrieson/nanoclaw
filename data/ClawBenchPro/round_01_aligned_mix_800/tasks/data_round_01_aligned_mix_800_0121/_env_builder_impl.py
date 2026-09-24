import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 原始库存数据：包含合格品、电池不合格、利润过低、产地非法、翻新机预埋
    data = [
        ["sku", "name", "category", "price", "cost", "battery_life_hr", "origin", "sn"],
        ["HT-001", "EcoWatch Pro", "Wearable", "299.0", "240.0", "48", "USA", "NEW-8821"], # 利润 < 15% (19.7%?) No, 59/299=19.7% -> OK
        ["HT-002", "DeepSleep Headband", "Health", "150.0", "130.0", "12", "China", "NEW-1102"], # 电池 < 24 & 利润 < 15% -> Bad
        ["HT-003", "HeartRate Plus", "Wearable", "199.0", "120.0", "10", "Japan*", "NEW-9901"], # 产地非法 & 电池 < 24 -> Bad
        ["HT-004", "PureAir Purifier", "Home", "450.0", "300.0", "168", "Canada", "REF-5501"], # 翻新机 (第3轮陷阱), 第一轮应通过(若不看SN)
        ["HT-005", "YogaSmart Mat", "Health", "89.0", "40.0", "72", "Unknown?", "NEW-4432"], # 产地非法 -> Bad
        ["HT-006", "BioRing", "Wearable", "250.0", "180.0", "30", "Germany", "NEW-2210"], # 合格 (利润28%) -> OK
        ["HT-007", "HydroFlask Smart", "Health", "50.0", "44.0", "120", "USA", "REF-1190"], # 利润 < 15% -> Bad
    ]
    
    with open("inventory/raw_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def build_turn_2():
    os.makedirs("new_arrivals", exist_ok=True)
    # Batch B: 涉及新规则（塑料占比）
    # 同时必须满足 Turn 1 的规则：电池 > 24, 利润 > 15%, 产地合法
    batch_b = [
        {
            "sku": "HT-008",
            "name": "ZenBuds",
            "battery_life_hr": 36,
            "price": 120.0,
            "cost": 80.0,
            "origin": "UK",
            "packaging": {"plastic_percent": 10, "paper_percent": 90},
            "sn": "NEW-7761"
        }, # 合格
        {
            "sku": "HT-009",
            "name": "StressSensor",
            "battery_life_hr": 40,
            "price": 200.0,
            "cost": 150.0,
            "origin": "France",
            "packaging": {"plastic_percent": 45, "paper_percent": 55},
            "sn": "NEW-3321"
        }, # 塑料超标 -> Bad
        {
            "sku": "HT-010",
            "name": "GlowLamp",
            "battery_life_hr": 5,
            "price": 100.0,
            "cost": 50.0,
            "origin": "Italy",
            "packaging": {"plastic_percent": 5, "paper_percent": 95},
            "sn": "NEW-0091"
        } # 电池不合格 -> Bad
    ]
    with open("new_arrivals/batch_B.json", "w") as f:
        json.dump(batch_b, f)

def build_turn_3():
    # 第三轮主要是逻辑剔除，不需要额外生成大量文件，但在 inventory 中追加一点干扰信息
    with open("inventory/vendor_notice.txt", "w") as f:
        f.write("URGENT: All units with SN prefix REF- are refurbished. Do not sell as new.")

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
