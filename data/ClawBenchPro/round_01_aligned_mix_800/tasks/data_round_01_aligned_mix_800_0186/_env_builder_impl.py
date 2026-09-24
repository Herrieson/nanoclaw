import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0186/turn_1
    os.makedirs("specifications", exist_ok=True)
    os.makedirs("proposals", exist_ok=True)
    
    # 基本要求
    with open("specifications/requirements.pdf", "w") as f:
        f.write("Total Budget: $250,000\nMinimum Horsepower: 100 HP\nMax Operating Hours: 8000\nMandatory: Maintenance record available.")

    # 供应商数据 - 设计陷阱：
    # ID_01: 便宜，但小时数接近极限，且是Tier 3 (第二轮会被刷掉)
    # ID_02: 价格适中，Tier 4，但无ADA阶梯 (第二轮会被刷掉)
    # ID_03: 贵，Tier 4, 有ADA，完美选型
    # ID_04: 价格极低，Tier 4, 有ADA，但工时造假 (第三轮会被刷掉)
    proposals = [
        {"id": "CAT-930K-01", "price": 75000, "hp": 150, "hours": 7800, "tier": "Tier 3", "ada": "No", "shipping": 2000, "brand": "Caterpillar"},
        {"id": "JD-544K-02", "price": 85000, "hp": 160, "hours": 4500, "tier": "Tier 4", "ada": "No", "shipping": 3000, "brand": "John Deere"},
        {"id": "KOM-WA320-03", "price": 120000, "hp": 170, "hours": 3200, "tier": "Tier 4", "ada": "Yes", "shipping": 5000, "brand": "Komatsu"},
        {"id": "CAT-950M-04", "price": 45000, "hp": 230, "hours": 1200, "tier": "Tier 4", "ada": "Yes", "shipping": 2500, "brand": "Caterpillar"}, # 陷阱：过分便宜
        {"id": "CASE-621G-05", "price": 95000, "hp": 172, "hours": 5000, "tier": "Tier 4", "ada": "Yes", "shipping": 4000, "brand": "Case"},
        {"id": "VOL-L60H-06", "price": 88000, "hp": 165, "hours": 5500, "tier": "Tier 4", "ada": "Yes", "shipping": 3500, "brand": "Volvo"}
    ]
    
    for p in proposals:
        with open(f"proposals/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_2():
    # 模拟 turn_2 发生的事情：某个低价好货被订走了
    # 实际上我们通过删除或修改文件来模拟
    target = "proposals/CAT-950M-04.json"
    if os.path.exists(target):
        os.rename(target, target + ".sold_out")

def build_turn_3():
    # 模拟 turn_3：发现造假数据
    os.makedirs("audit", exist_ok=True)
    os.makedirs("final_report", exist_ok=True)
    
    # 审计报告指出：VOL-L60H-06 虽然看起来很好，但实际工时被调过
    with open("audit/anomalous_logs.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Serial_Number", "Reported_Hours", "Actual_Estimated_Hours", "Note"])
        writer.writerow(["VOL-L60H-06", "5500", "8200", "ECU mismatch detected"])
        writer.writerow(["CASE-621G-05", "5000", "5100", "Normal wear"])

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
