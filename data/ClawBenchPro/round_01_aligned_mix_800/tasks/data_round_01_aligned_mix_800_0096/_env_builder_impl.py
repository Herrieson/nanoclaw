import os
import argparse
import json
import csv

def build_turn_1():
    # 路径已在 assets/data_round_01_aligned_mix_800_0096/turn_1
    os.makedirs("raw_manifests", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 1. 混合格式的货位清单
    # CSV 包含脏数据和价格冲突
    with open("raw_manifests/manager_a_report.csv", "w") as f:
        f.write("sku,category,price,frequency,supplier\n")
        f.write("TECH-99,Electronics,500,0.85,AlphaTech\n") # 重叠项1
        f.write("SOFT-01,Furniture,120,0.3,GlobalWood\n")
        f.write("TECH-102,Electronics,800,0.92,BetaSystems\n")
        
    with open("raw_manifests/manager_b_report.json", "w") as f:
        json.dump([
            {"sku": "TECH-99", "category": "Electronics", "price": 550, "frequency": 0.85, "supplier": "AlphaTech"}, # 价格冲突: 500 vs 550
            {"sku": "TECH-404", "category": "Electronics", "price": 300, "frequency": 0.1, "supplier": "CheapWires"}
        ], f)

    # 2. 仓库规格配置文件
    with open("warehouse_specs.conf", "w") as f:
        f.write("[Section_A]\n")
        f.write("total_volume_units = 1000\n")
        f.write("safety_threshold = 0.3\n")
        f.write("incompatible_standards = ['Zigbee', 'Legacy-RF']\n") # 预埋技术陷阱

def build_turn_2():
    # 路径已在 assets/data_round_01_aligned_mix_800_0096/turn_2
    os.makedirs("new_regulations", exist_ok=True)
    
    # 注入环境评分，BetaSystems 评分很高但 AlphaTech 踩线
    with open("new_regulations/environmental_impact.csv", "w") as f:
        f.write("supplier_name,carbon_score,is_certified\n")
        f.write("AlphaTech,58,True\n") # 低于 60
        f.write("BetaSystems,85,True\n")
        f.write("GlobalWood,70,True\n")
        f.write("CheapWires,40,False\n")

def build_turn_3():
    # 路径已在 assets/data_round_01_aligned_mix_800_0096/turn_3
    os.makedirs("emergency_inbound", exist_ok=True)
    
    # 模拟文件损坏（删掉 turn_1 的一个核心文件，逼迫 agent 使用之前的 memory/deliverables）
    if os.path.exists("raw_manifests/manager_a_report.csv"):
        os.remove("raw_manifests/manager_a_report.csv")
    
    # 新样品数据，带有技术陷阱
    with open("emergency_inbound/samples.json", "w") as f:
        json.dump([
            {
                "id": "NEW-TECH-01", 
                "name": "Smart-Hub-X", 
                "standard": "Zigbee", # 违反 turn_1 埋下的 Zigbee 禁令
                "supplier": "BetaSystems"
            },
            {
                "id": "NEW-TECH-02", 
                "name": "Eco-Sensor", 
                "standard": "Matter", 
                "supplier": "AlphaTech" # 虽然技术 OK，但供应商在 turn_2 被环保否决
            },
            {
                "id": "NEW-TECH-03", 
                "name": "Solar-Link", 
                "standard": "Matter", 
                "supplier": "BetaSystems" # 唯一应该通过的
            }
        ], f)

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
