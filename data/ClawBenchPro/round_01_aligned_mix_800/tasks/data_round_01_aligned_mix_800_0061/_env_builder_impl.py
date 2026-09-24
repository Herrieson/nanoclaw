import os
import argparse
import json
import csv
import random

def build_turn_1():
    # 模拟物流公司的原始数据环境
    os.makedirs("manifests", exist_ok=True)
    os.makedirs("regulations", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 跨境法规文件
    with open("regulations/import_rules.txt", "w", encoding="utf-8") as f:
        f.write("Region_A -> Region_B: Max weight 50kg per parcel. No lithium batteries exceeding 100Wh.\n")
        f.write("Region_A -> Region_C: Duty-free under $800. Restricted items: Fine Art, Seeds.\n")
        f.write("Urgent: All shipments to Region_B must have a 'SECURE_SCAN' tag if containing electronics.\n")

    # 2. 货运清单 (包含脏数据和逻辑陷阱)
    manifest_data = [
        ["ID", "Origin", "Dest", "Weight_kg", "Value_USD", "Contents", "Battery_Wh"],
        ["PKG_001", "Region_A", "Region_B", "45", "1200", "Laptops", "95"], # 需SECURE_SCAN
        ["PKG_002", "Region_A", "Region_C", "10", "1500", "Oil Painting", "0"], # 违禁: Fine Art
        ["PKG_003", "Region_A", "Region_B", "55", "300", "Books", "0"], # 超重: 55kg > 50kg
        ["PKG_004", "Region_A", "Region_C", "5", "750", "Apparel", "0"], # 合规
        ["PKG_005", "Region_A", "Region_B", "12", "500", "Tablets", "120"], # 违禁: Battery > 100Wh
        ["PKG_006", "Region_A", "Region_B", "48", "900", "Kitchenware", "0"], # 合规
    ]
    with open("manifests/pending_shipments.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(manifest_data)

def build_turn_2():
    # 注入新的突发订单，且包含与第一轮规则微妙冲突的情况
    os.makedirs("incoming", exist_ok=True)
    
    # 新订单 PKG_007: 看起来符合 Region_B 规则（49kg），但实际上第二轮 Prompt 会引入新的燃油限制
    new_data = [
        ["ID", "Origin", "Dest", "Weight_kg", "Value_USD", "Contents", "Battery_Wh"],
        ["PKG_007", "Region_A", "Region_B", "49", "2100", "Server Components", "80"],
        ["PKG_008", "Region_A", "Region_C", "2", "100", "Dried Mango", "0"], # 种子/植物制品争议项
    ]
    with open("incoming/new_batch.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_data)

def build_turn_3():
    # 模拟一个外部审计文件，质疑之前的决定
    os.makedirs("audit", exist_ok=True)
    with open("audit/query.json", "w") as f:
        json.dump({
            "query_id": "AUDIT_99",
            "subject": "Inconsistent weight calculation for Region_B",
            "context": "We received reports that the scale in Region_A was miscalibrated by +2kg for all items over 40kg."
        }, f)

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
