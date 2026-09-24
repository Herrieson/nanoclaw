import os
import argparse
import json
import random

def build_turn_1():
    # 建立初始育种候选池
    os.makedirs("records/pedigree", exist_ok=True)
    os.makedirs("records/health_logs", exist_ok=True)
    os.makedirs("delivery", exist_ok=True)

    # 模拟 10 头候选牛的基因与健康数据
    # 设定：我们需要高产奶量(Milk_Yield > 800)且基因指数(Gen_Idx > 0.85)的组合
    cows = [
        {"id": "COW_001", "milk_yield": 850, "gen_idx": 0.92, "cost": 12000, "ancestry": "Line_A"},
        {"id": "COW_002", "milk_yield": 780, "gen_idx": 0.88, "cost": 9000, "ancestry": "Line_B"},
        {"id": "COW_003", "milk_yield": 920, "gen_idx": 0.86, "cost": 15000, "ancestry": "Line_A"},
        {"id": "COW_004", "milk_yield": 810, "gen_idx": 0.89, "cost": 11000, "ancestry": "Line_C"},
        {"id": "COW_005", "milk_yield": 860, "gen_idx": 0.84, "cost": 9500, "ancestry": "Line_B"}, # 基因略低
        {"id": "COW_006", "milk_yield": 880, "gen_idx": 0.87, "cost": 13000, "ancestry": "Line_D"},
        {"id": "COW_007", "milk_yield": 950, "gen_idx": 0.95, "cost": 18000, "ancestry": "Line_D"}, # 最优但最贵
        {"id": "COW_008", "milk_yield": 700, "gen_idx": 0.70, "cost": 5000, "ancestry": "Line_E"},
        {"id": "COW_009", "milk_yield": 830, "gen_idx": 0.86, "cost": 10500, "ancestry": "Line_C"},
        {"id": "COW_010", "milk_yield": 890, "gen_idx": 0.91, "cost": 14000, "ancestry": "Line_E"},
    ]
    
    for cow in cows:
        with open(f"records/pedigree/{cow['id']}.json", "w") as f:
            json.dump(cow, f)
            
    # 健康日志（干扰项：某些牛有潜在遗传病史）
    health_status = {
        "COW_001": "Stable",
        "COW_002": "Stable",
        "COW_003": "Carrier_of_BLAD", # 遗传病携带者，不能选
        "COW_004": "Stable",
        "COW_005": "Stable",
        "COW_006": "Stable",
        "COW_007": "History_of_Mastitis", # 曾患乳腺炎，高风险
        "COW_008": "Stable",
        "COW_009": "Stable",
        "COW_010": "Carrier_of_DUMPS", # 遗传病
    }
    
    for cid, status in health_status.items():
        with open(f"records/health_logs/{cid}_status.txt", "w") as f:
            f.write(f"Condition: {status}\nLast Check: 2023-10-12")

def build_turn_2():
    # 模拟新的市场约束：由于饲料成本上涨，单头购买成本不能超过 13000
    # 此阶段无需新建复杂文件，只需确保之前的目录存在
    os.makedirs("updates", exist_ok=True)
    with open("updates/market_flash.txt", "w") as f:
        f.write("URGENT: Feed prices surging. Procurement cap adjusted to 13,000 per unit. \n"
                "Also, we suspect environmental sensitivity in Line_D. Minimize Line_D exposure.")

def build_turn_3():
    # 模拟第三方实验室送来的交叉比对报告，揭示了某些牛的基因指数是误报
    # Agent 需要根据这个新文件，推翻之前的结论
    with open("updates/lab_audit.csv", "w") as f:
        f.write("Cow_ID,Corrected_Gen_Idx,Note\n")
        f.write("COW_001,0.72,Lab error in previous sequencing\n") # 001 之前是 0.92，现在不合格了
        f.write("COW_004,0.91,Re-verified\n")
        f.write("COW_009,0.88,Upgraded index\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1: build_turn_1()
    elif args.turn == 2: build_turn_2()
    elif args.turn == 3: build_turn_3()
