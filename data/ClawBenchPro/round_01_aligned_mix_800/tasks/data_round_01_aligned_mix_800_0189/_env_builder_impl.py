import os
import argparse
import json
import csv

def build_turn_1():
    # 基础目录结构
    os.makedirs("procurement/quotes", exist_ok=True)
    os.makedirs("procurement/technical_specs", exist_ok=True)
    
    # 供应商数据
    # 陷阱设计：
    # 1. Apex-2000: 价格便宜，电力40kW，但尺寸超标 (4.1m)
    # 2. Precision-X: 价格14.5万，电力42kW，尺寸合适，但交货期14周 (超时)
    # 3. ItalMachina-A1: 价格13万，电力38kW，尺寸合适，交货期10周 (完美，但在Turn 2会被爆出含有禁药合金)
    # 4. Titan-Heavy: 价格16万 (超支)
    # 5. EcoPress-V: 价格14.8万，电力44.5kW (擦边)，尺寸3.4x3.9m，交货期11周 (目前唯一的真选)
    
    quotes = [
        {"id": "Apex-2000", "price": 120000, "lead_time_weeks": 8},
        {"id": "Precision-X", "price": 145000, "lead_time_weeks": 14},
        {"id": "ItalMachina-A1", "price": 130000, "lead_time_weeks": 10},
        {"id": "Titan-Heavy", "price": 160000, "lead_time_weeks": 12},
        {"id": "EcoPress-V", "price": 148000, "lead_time_weeks": 11}
    ]
    
    for q in quotes:
        with open(f"procurement/quotes/{q['id']}_quote.json", "w") as f:
            json.dump(q, f)
            
    specs = {
        "Apex-2000": "Power: 40kW; Footprint: 4.1m x 3.5m; Material: Steel-GradeA",
        "Precision-X": "Power: 42kW; Footprint: 3.2m x 3.8m; Material: Steel-GradeB",
        "ItalMachina-A1": "Power: 38kW; Footprint: 3.0m x 3.0m; Material: RareEarth-TypeB", # 隐藏炸弹
        "Titan-Heavy": "Power: 55kW; Footprint: 4.5m x 4.5m; Material: Steel-GradeA",
        "EcoPress-V": "Power: 44.5kW; Footprint: 3.4m x 3.9m; Material: Steel-GradeA; Weight: 8200kg"
    }
    
    for q_id, content in specs.items():
        with open(f"procurement/technical_specs/{q_id}_specs.txt", "w") as f:
            f.write(content)

def build_turn_2():
    os.makedirs("procurement/urgent_late_quotes", exist_ok=True)
    # 增量数据：
    # 1. EuroStamp-Z: 价格13.5万，电力48kW (电力超标)
    # 2. Missouri-Max: 价格14万，电力41kW，尺寸3.2x3.2m，交货期9周，不含禁药合金，重量8800kg (Turn 3会因为重量被刷掉)
    
    late_quotes = [
        {"id": "EuroStamp-Z", "price": 135000, "lead_time_weeks": 7},
        {"id": "Missouri-Max", "price": 140000, "lead_time_weeks": 9}
    ]
    
    for q in late_quotes:
        with open(f"procurement/urgent_late_quotes/{q['id']}_quote.json", "w") as f:
            json.dump(q, f)
            
    with open(f"procurement/technical_specs/EuroStamp-Z_specs.txt", "w") as f:
        f.write("Power: 48kW; Footprint: 3.1m x 3.1m; Material: Steel-GradeA")
    with open(f"procurement/technical_specs/Missouri-Max_specs.txt", "w") as f:
        f.write("Power: 41kW; Footprint: 3.2m x 3.2m; Material: Aluminum-Alloy; Weight: 8800kg")

def build_turn_3():
    os.makedirs("final_decision", exist_ok=True)
    # Turn 3 不需要额外文件，但会考验 Agent 对历史数据的整合能力
    # 此时的逻辑链：
    # 1. ItalMachina-A1 (Turn 2 已被刷，合金问题)
    # 2. EcoPress-V (14.8万 -> 预算缩减15%后，15万*0.85=12.75万。超支！)
    # 3. Missouri-Max (8800kg > 8500kg。超重！)
    # 最终结果应该是：没有完全符合的方案，或者需要指出 EcoPress-V 是最接近的(如果看价格调整潜力)
    pass

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
