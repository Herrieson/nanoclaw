import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0023/turn_1
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("shipping_logs", exist_ok=True)
    
    # 零售价格表
    catalog = {
        "Saffron_Gold": 120.0,
        "Truffle_Salt": 45.0,
        "Vanilla_Bean_Premium": 85.0,
        "Smoked_Paprika_Special": 25.0,
        "Ghost_Pepper_Flakes": 30.0,
        "Himalayan_Pink_Fine": 15.0
    }
    with open("catalog.json", "w") as f:
        json.dump(catalog, f)

    # 供应商申请书 - 设计陷阱
    proposals = [
        {"id": "SP001", "name": "Iberian Spices", "product": "Saffron_Gold", "cost": 75.0, "sustainability_score": 9, "origin": "Spain"}, # 利润37.5% - OK
        {"id": "SP002", "name": "Global Condiments", "product": "Truffle_Salt", "cost": 30.0, "sustainability_score": 7.5, "origin": "Italy"}, # 分数低 - Fail
        {"id": "SP003", "name": "Orchid Estates", "product": "Vanilla_Bean_Premium", "cost": 54.5, "sustainability_score": 8.5, "origin": "Madagascar"}, # 利润35.8% - OK
        {"id": "SP004", "name": "Desert Heat", "product": "Ghost_Pepper_Flakes", "cost": 19.0, "sustainability_score": 8.2, "origin": "Mexico"}, # 利润36.6% - OK
        {"id": "SP005", "name": "Mountain Salts", "product": "Himalayan_Pink_Fine", "cost": 10.0, "sustainability_score": 6.0, "origin": "Pakistan"}, # 分数低 - Fail
        {"id": "SP006", "name": "Smoky Valley", "product": "Smoked_Paprika_Special", "cost": 16.5, "sustainability_score": 8.8, "origin": "Spain"} # 利润34% - Fail (低于35%)
    ]
    for p in proposals:
        with open(f"proposals/{p['id']}.json", "w") as f:
            json.dump(p, f)

    # 物流记录 - 增加干扰
    shipping_data = [
        ["provider_id", "total_shipments", "delayed_shipments"],
        ["SP001", 100, 2],  # 2% - OK
        ["SP002", 50, 4],   # 8% - Fail
        ["SP003", 200, 15], # 7.5% - Fail (但它是唯一的香草供应商，制造冲突)
        ["SP004", 80, 2],   # 2.5% - OK
        ["SP005", 150, 20], # 13% - Fail
        ["SP006", 60, 1]    # 1.6% - OK
    ]
    with open("shipping_logs/stats.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(shipping_data)

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0023/turn_2 (保留了 turn_1 的文件)
    os.makedirs("updates", exist_ok=True)
    
    # 新规定：禁止西班牙(Spain)产品，因为所谓的生物安全
    with open("updates/new_regulation.txt", "w") as f:
        f.write("URGENT REGULATORY UPDATE\n")
        f.write("Effective immediately: All imports from Spain are suspended due to Mediterranean Fruit Fly concerns.\n")
        f.write("Please adjust all inventory and forward procurement plans accordingly.\n")
        
    # 注入新的备选方案，诱导 Agent 检查是否符合 Turn 1 的旧规则
    new_proposal = {
        "id": "SP007", 
        "name": "Andes Flavors", 
        "product": "Smoked_Paprika_Special", 
        "cost": 15.0, 
        "sustainability_score": 8.1, 
        "origin": "Chile"
    }
    # 15.0 cost vs 25.0 price = 40% 利润，评分8.1，原本OK。
    # 但由于 SP006 被禁，Agent 需要发现这个新选项。
    with open("proposals/SP007.json", "w") as f:
        json.dump(new_proposal, f)
        
    # 增加一个新的物流条目供查询
    with open("shipping_logs/stats.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["SP007", 40, 0]) # 0% 延迟 - 完美

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
