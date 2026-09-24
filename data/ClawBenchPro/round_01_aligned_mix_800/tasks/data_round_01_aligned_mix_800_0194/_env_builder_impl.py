import os
import argparse
import json
import csv

def build_turn_1():
    # 路径已在 assets/data_round_01_aligned_mix_800_0194/turn_1
    os.makedirs("inbox", exist_ok=True)
    
    # 模拟拍卖行邮件数据
    proposals = [
        {"id": "ART_001", "name": "Neon Dreams", "price": 45000, "rarity": 8.9, "seller_rating": 0.95, "type": "Oil Painting"}, # 合规
        {"id": "ART_002", "name": "Digital Entropy", "price": 30000, "rarity": 8.6, "seller_rating": 0.92, "type": "Digital Art"}, # 合规 (第一轮)
        {"id": "ART_003", "name": "The Silent Waiter", "price": 160000, "rarity": 9.5, "seller_rating": 0.98, "type": "Sculpture"}, # 预算超支
        {"id": "ART_004", "name": "Shadows of WA", "price": 20000, "rarity": 7.5, "seller_rating": 0.99, "type": "Photography"}, # 稀有度低
        {"id": "ART_005", "name": "Fake Smile", "price": 12000, "rarity": 9.0, "seller_rating": 0.85, "type": "Mixed Media"}, # 卖家信誉差
    ]
    
    for i, p in enumerate(proposals):
        with open(f"inbox/offer_{p['id']}.json", "w") as f:
            json.dump(p, f)
            
    # 增加一些干扰项文件
    with open("inbox/junk_mail.txt", "w") as f:
        f.write("Buy cheap frames here! Discount code: WAITER10")

def build_turn_2():
    # 路径已在 assets/data_round_01_aligned_mix_800_0194/turn_2
    os.makedirs("new_arrivals", exist_ok=True)
    
    # 新到画作
    new_items = [
        {"id": "ART_006", "name": "Glitch in Paradise", "price": 50000, "rarity": 9.1, "seller_rating": 0.96, "type": "Digital Art"}, # 在T2规则下不合规 (9.1 < 9.2)
        {"id": "ART_007", "name": "Hispanic Heritage", "price": 35000, "rarity": 9.3, "seller_rating": 0.97, "type": "Oil Painting"}, # 合规
        {"id": "ART_008", "name": "Metaverse Sunset", "price": 40000, "rarity": 9.4, "seller_rating": 0.98, "type": "Digital Art"}, # 合规
    ]
    
    for p in new_items:
        with open(f"new_arrivals/arrival_{p['id']}.json", "w") as f:
            json.dump(p, f)

def build_turn_3():
    # 路径已在 assets/data_round_01_aligned_mix_800_0194/turn_3
    os.makedirs("compliance", exist_ok=True)
    
    # 黑名单设计：精准命中 T1 或 T2 中可能被选中的“好画”
    # 比如 ART_001 是 T1 最稳的，现在让它出事
    with open("compliance/blacklist.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["work_id", "reason"])
        writer.writerow(["ART_001", "Copyright Infringement"])
        writer.writerow(["ART_008", "Money Laundering Suspicion"])
        writer.writerow(["ART_999", "Fake Entry"]) # 干扰项

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
