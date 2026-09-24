import os
import argparse
import json
import csv

def build_turn_1():
    # 建立目录结构
    os.makedirs("incoming_artifacts", exist_ok=True)
    os.makedirs("security_protocols", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 安全协议文件 (包含隐性阈值)
    protocols = {
        "max_insurance_value": 50000,
        "fragility_levels": ["Low", "Medium", "High", "Extreme"],
        "forbidden_regions": ["Conflict-Zone-A", "Unknown"]
    }
    with open("security_protocols/global_rules.json", "w") as f:
        json.dump(protocols, f)

    # 2. 原始申请表 (混合格式)
    # A组: 正常 JSON
    artifact_a = [
        {"id": "ART_001", "name": "Jade Dragon", "origin": "East Asia", "value": 12000, "fragility": "High", "group_id": "G1"},
        {"id": "ART_002", "name": "Stone Tablet", "origin": "Egypt", "value": 48000, "fragility": "Medium", "group_id": None}, # 接近上限
        {"id": "ART_003", "name": "Ancient Coin", "origin": "Conflict-Zone-A", "value": 500, "fragility": "Low", "group_id": None}  # 产地禁令
    ]
    with open("incoming_artifacts/batch_china.json", "w") as f:
        json.dump(artifact_a, f)

    # B组: CSV (包含组合件)
    with open("incoming_artifacts/batch_europe.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "origin", "value", "fragility", "group_id"])
        writer.writerow(["ART_004", "Silver Sword", "Europe", "25000", "Medium", "G2"])
        writer.writerow(["ART_005", "Silver Scabbard", "Europe", "30000", "Low", "G2"]) # G2总和 55000, 超过 50000 阈值
        writer.writerow(["ART_006", "Glass Vial", "Rome", "8000", "Extreme", None])

    # C组: 脏数据 TXT
    with open("incoming_artifacts/notes_misc.txt", "w") as f:
        f.write("id:ART_007|name:Clay Jar|origin:Unknown|value:200|fragility:Low|group_id:None\n") # Unknown 禁令
        f.write("id:ART_008|name:Golden Mask|origin:Peru|value:15000|fragility:High|group_id:None\n")

def build_turn_2():
    # 模拟 turn_2 增量数据
    os.makedirs("new_shipment", exist_ok=True)
    
    # 1. 冲突配置文件
    conflicts = [
        {"type": "origin_overlap", "rule": "Same origin items cannot exceed 2 in the same batch", "priority": "score_based"}
    ]
    with open("conflicts.json", "w") as f:
        json.dump(conflicts, f)

    # 2. 新到的挑战件
    # 其中 ART_009 的产地 Peru 与 ART_008 重复
    # 其中 ART_010 的价值 45000，在第一轮合规，但在第二轮下调 15% (50000*0.85=42500) 后不合规
    new_data = [
        {"id": "ART_009", "name": "Peru Textile", "origin": "Peru", "value": 5000, "fragility": "High", "group_id": None},
        {"id": "ART_010", "name": "Greek Statue", "origin": "Greece", "value": 45000, "fragility": "Medium", "group_id": None}
    ]
    with open("new_shipment/late_arrivals.json", "w") as f:
        json.dump(new_data, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
