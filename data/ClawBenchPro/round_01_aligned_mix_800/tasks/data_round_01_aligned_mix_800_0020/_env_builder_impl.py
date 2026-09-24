import os
import argparse
import csv
import json

def build_turn_1():
    # 建立目录结构
    os.makedirs("procurement/quotes", exist_ok=True)
    os.makedirs("recruitment", exist_ok=True)
    os.makedirs("standards", exist_ok=True)

    # 1. 供应商报价数据 - 包含陷阱
    # 方案 A: 便宜但耐用度低
    # 方案 B: 质量极好但价格贵
    # 方案 C: 中间地带，且是唯一的正确解（需精确组合）
    quotes = {
        "Vendor_Alpha": [
            {"item": "Treadmill_X1", "price": 4000, "durability": 9.2, "stock": 10},
            {"item": "Weight_Set_A", "price": 2000, "durability": 8.0, "stock": 5}
        ],
        "Vendor_Beta": [
            {"item": "Treadmill_Y2", "price": 3500, "durability": 8.1, "stock": 10},
            {"item": "Weight_Set_B", "price": 1500, "durability": 8.6, "stock": 5}
        ],
        "Vendor_Gamma": [
            {"item": "Treadmill_Z3", "price": 4500, "durability": 8.8, "stock": 4}, # 库存不足 5 台的陷阱
            {"item": "Weight_Set_C", "price": 1800, "durability": 8.7, "stock": 10}
        ]
    }
    for v, items in quotes.items():
        with open(f"procurement/quotes/{v}.json", "w") as f:
            json.dump(items, f)

    # 2. 教练名单 - 包含复杂资质
    trainers = [
        ["name", "certifications", "base_salary", "experience_years", "score"],
        ["Alice", "NASM,CPT,CPR", 5000, 5, 9.5],
        ["Bob", "ACE,CPR", 4500, 3, 8.2],
        ["Charlie", "NASM,CPT", 4800, 4, 8.8], # 缺 CPR
        ["David", "NASM,CPT,CPR,LI_2024", 5200, 6, 9.1], # LI 为后续轮次伏笔
        ["Eve", "ACE,CPR,LI_2023", 4200, 2, 7.5]
    ]
    with open("recruitment/trainers.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(trainers)

    # 3. 资质标准
    with open("standards/certifications.txt", "w") as f:
        f.write("Standard HIIT Trainer Requirements:\n1. Must hold either NASM or ACE certification.\n2. Must hold valid CPR certification.\n3. Base salary must be within market range.")

def build_turn_2():
    # 模拟时间推进，注入增量数据
    os.makedirs("procurement/updates", exist_ok=True)
    
    # 供应链警报：Vendor_Beta (第一轮中最优的廉价选项) 挂了
    alert = {
        "status": "CRITICAL",
        "affected_vendors": ["Vendor_Beta"],
        "reason": "Logistics Strike",
        "expected_delay": "90 days"
    }
    with open("procurement/updates/supply_chain_alert.json", "w") as f:
        json.dump(alert, f)

    # 法律更新：要求 Liability Insurance (LI) 必须是 2024 版本
    with open("standards/legal_update_v2.txt", "w") as f:
        f.write("New Regulatory Compliance:\nStarting this month, all active trainers must present Liability Insurance (LI) documentation specifically tagged as LI_2024. Older versions (e.g., LI_2023) are no longer accepted.")

def build_turn_3():
    # 增加一名新供应商，提供耐用度稍低但价格极低的选项，作为 Turn 3 预算缩减后的救命稻草
    os.makedirs("procurement/quotes", exist_ok=True)
    budget_saver = [
        {"item": "Treadmill_Budget", "price": 2800, "durability": 8.0, "stock": 10},
        {"item": "Weight_Set_Budget", "price": 1000, "durability": 8.1, "stock": 10}
    ]
    with open("procurement/quotes/Vendor_Budget.json", "w") as f:
        json.dump(budget_saver, f)

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
