import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟手工艺人的混乱工作区
    os.makedirs("inventory/beads", exist_ok=True)
    os.makedirs("inventory/findings", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("records", exist_ok=True)

    # 珠子库存：由于是手工制作，规格极其细碎
    beads_data = [
        ["sku", "material", "size_mm", "color", "quantity", "unit_cost"],
        ["B-SEED-001", "Glass", "2.0", "Turquoise", "5000", "0.02"],
        ["B-SEED-002", "Glass", "2.0", "Coral Red", "1200", "0.02"],
        ["B-SHELL-01", "Abalone", "8.0", "Iridescent", "45", "1.50"], # 数量告急
        ["B-BONE-05", "Bison Bone", "10.0", "Natural White", "200", "0.80"],
        ["B-SILV-09", "Sterling Silver", "4.0", "Polished", "15", "4.20"] # 极少
    ]
    with open("inventory/beads/current_stock.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(beads_data)

    # 供应商列表：包含各种复杂的评价和限制
    vendors = {
        "Rainier_Supplies": {
            "rating": 4.8,
            "specialty": "Traditional Materials",
            "min_order": 200,
            "shipping_days": 5,
            "discounts": "10% off for orders over $500",
            "notes": "They only source ethical abalone. Very strict on tribal certification."
        },
        "Olympic_Wholesale": {
            "rating": 3.5,
            "specialty": "Bulk Glass Beads",
            "min_order": 50,
            "shipping_days": 2,
            "notes": "Fast but quality varies. Sometimes sends plastic instead of glass."
        },
        "Seattle_Silver_Smith": {
            "rating": 5.0,
            "specialty": "Precious Metals",
            "min_order": 0,
            "shipping_days": 7,
            "notes": "Premium quality. Prices are 20% higher than market but they are local."
        }
    }
    with open("vendors/directory.json", "w") as f:
        json.dump(vendors, f, indent=4)

    # 展会需求
    orders = [
        {"item": "Salish Sea Necklace", "beads_needed": {"B-SHELL-01": 10, "B-SILV-09": 4, "B-SEED-001": 200}, "quantity_to_make": 10},
        {"item": "Bison Spirit Bracelet", "beads_needed": {"B-BONE-05": 5, "B-SEED-002": 50}, "quantity_to_make": 15}
    ]
    with open("records/upcoming_fair_needs.json", "w") as f:
        json.dump(orders, f, indent=4)

def build_turn_2():
    # 注入突发环境变化：西雅图暴雨导致物流中断
    os.makedirs("alerts", exist_ok=True)
    with open("alerts/shipping_update.txt", "w") as f:
        f.write("URGENT: Heavy flooding near Rainier Pass. All shipments from Rainier_Supplies are delayed by at least 15 business days.\n")
        f.write("Olympic_Wholesale reports no delays but their inventory of Abalone is currently OUT OF STOCK.")

def build_turn_3():
    # 第三轮：客户定制化需求与历史规则冲突
    os.makedirs("custom_orders", exist_ok=True)
    # 增加一个特殊的定制文件
    custom_request = {
        "client": "Chief's Legacy Gallery",
        "request": "30 extra Abalone Shell necklaces. Must use traditional certified shells. No plastic substitutes allowed.",
        "deadline": "7 days"
    }
    with open("custom_orders/gallery_request.json", "w") as f:
        json.dump(custom_request, f, indent=4)

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
