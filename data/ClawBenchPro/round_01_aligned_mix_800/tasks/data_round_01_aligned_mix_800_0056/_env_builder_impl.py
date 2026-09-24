import os
import argparse
import json
import csv

def build_turn_1():
    # 初始库存，包含脏数据和复杂逻辑
    os.makedirs("inventory", exist_ok=True)
    inventory = [
        ["id", "item_name", "category", "condition_score", "base_price", "weight_oz"],
        ["V-001", "1950s Wool Blazer", "Outerwear", "4.5", "120.00", "45"],
        ["V-002", "Vintage Denim Overalls", "Workwear", "2.8", "85.00", "52"], # 评分低于3，应维修
        ["V-003", "Silk Patterned Tie", "Accessory", "5.0", "35.00", "4"],
        ["V-004", "1940s Leather Boots", "Footwear", "3.2", "150.00", "64"],
        ["V-005", "Union Made Work Shirt", "Workwear", "4.8", "55.00", "12"],
        ["V-006", "Distressed Leather Jacket", "Outerwear", "2.5", "200.00", "80"], # 应维修
    ]
    with open("inventory/raw_list.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

    # 运费政策：逻辑复杂化
    os.makedirs("mailbox", exist_ok=True)
    with open("shipping_policy.txt", "w") as f:
        f.write("SHIPPING RULES:\n")
        f.write("1. Base rate: $5.00 for anything under 16oz.\n")
        f.write("2. Heavy items (16oz+): $5.00 + $0.50 per additional 4oz.\n")
        f.write("3. Outerwear surcharge: Add $3.00 flat.\n")
        f.write("4. Orders over $150 get 10% discount on the items, but NOT the shipping.\n")

    # 邮件询价
    os.makedirs("mailbox/inquiries", exist_ok=True)
    with open("mailbox/inquiries/inquiry_1.txt", "w") as f:
        f.write("From: John\nSubject: Need a blazer\nI want the 1950s Wool Blazer (V-001). How much with shipping to SC?")
    
    with open("mailbox/inquiries/inquiry_2.txt", "w") as f:
        f.write("From: Sarah\nSubject: Workwear bundle\nInterested in V-002 and V-005. Can you give me a total?")

def build_turn_2():
    # 模拟增量数据
    os.makedirs("inventory", exist_ok=True)
    new_arrivals = [
        {"id": "V-007", "item_name": "1960s Fedora", "category": "Accessory", "condition_score": 4.9, "base_price": 75.00, "weight_oz": 10},
        {"id": "V-001", "item_name": "1950s Wool Blazer (Duplicate)", "category": "Outerwear", "condition_score": 4.0, "base_price": 110.00, "weight_oz": 45} # 冲突项
    ]
    with open("inventory/new_arrivals.json", "w") as f:
        json.dump(new_arrivals, f)

    # 运费规则变更
    os.makedirs("mailbox/updates", exist_ok=True)
    with open("mailbox/updates/logistics_alert.pdf.txt", "w") as f:
        f.write("URGENT: Fuel surcharge update.\n")
        f.write("Effective immediately, the base rate for all shipments is now $7.50 (was $5.00).\n")
        f.write("Heavy item additional fee is now $0.75 per 4oz (was $0.50).\n")
        f.write("The 10% discount on orders over $150 now applies to BOTH items and shipping.")

def build_turn_3():
    # 客户投诉
    os.makedirs("mailbox/disputes", exist_ok=True)
    with open("mailbox/disputes/customer_04.txt", "w") as f:
        f.write("Hi Arthur, I bought the V-004 boots. You charged me based on the old shipping price but applied the new discount rule? Or was it the other way? The math is wrong. Please check the V-004 total price.")

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
