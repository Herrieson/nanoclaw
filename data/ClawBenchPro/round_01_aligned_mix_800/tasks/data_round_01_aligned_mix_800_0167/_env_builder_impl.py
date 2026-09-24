import os
import argparse
import json
import random

def build_turn_1():
    # 路径已由框架设定为 assets/data_round_01_aligned_mix_800_0167/turn_1
    os.makedirs("raw_assets", exist_ok=True)
    
    # 模拟传感器日志，混合了正常、高故障、昂贵、以及特殊捐赠设备
    # 关键逻辑：价格 > 1500 且 故障率 > 5% 报废，除非 Origin 为 "Donation_India"
    assets = [
        {"id": "SNS-001", "type": "Quantum_Gate", "price": 1200, "failure_rate": 0.02, "origin": "Purchased", "power": 150},
        {"id": "SNS-002", "type": "Quantum_Gate", "price": 1800, "failure_rate": 0.08, "origin": "Purchased", "power": 200}, # 报废项
        {"id": "SNS-003", "type": "Cryo_Sensor", "price": 2500, "failure_rate": 0.12, "origin": "Donation_India", "power": 300}, # 需维护（特权）
        {"id": "SNS-004", "type": "Laser_Ref", "price": 900, "failure_rate": 0.06, "origin": "Purchased", "power": 80},
        {"id": "SNS-005", "type": "Quantum_Gate", "price": 2200, "failure_rate": 0.01, "origin": "Purchased", "power": 180},
    ]
    
    with open("raw_assets/inventory.json", "w") as f:
        json.dump(assets, f, indent=2)
    
    # 混淆文件
    with open("raw_assets/README.txt", "w") as f:
        f.write("Old notes: Remember to check the liquid nitrogen levels. The Indian sensors are a bit flaky but the boss loves them.")

def build_turn_2():
    # 路径已由框架设定为 assets/data_round_01_aligned_mix_800_0167/turn_2 (保留了 turn_1 的产物)
    os.makedirs("new_proposals", exist_ok=True)
    
    # 供应商方案：需根据 turn_1 计算的平均功耗 (150+200+300+80+180)/5 = 182, 80% = 145.6
    # 且受限于 12000 预算，以及 turn_1 设定的 1500/5% 红线
    proposals = [
        {
            "provider": "QuantumTech",
            "model": "QT-Alpha",
            "price": 11500,
            "est_failure_rate": 0.04,
            "power_consumption": 140, # 完美匹配：价格、故障率、功耗
            "specs": "High precision, low heat"
        },
        {
            "provider": "DeepCold",
            "model": "DC-Zero",
            "price": 8000,
            "est_failure_rate": 0.07, # 失败：故障率 > 5%
            "power_consumption": 130,
            "specs": "Affordable but risky"
        },
        {
            "provider": "FutureDynamics",
            "model": "FD-Gen2",
            "price": 13000, # 失败：预算超支
            "est_failure_rate": 0.02,
            "power_consumption": 120,
            "specs": "Best performance"
        }
    ]
    
    for i, p in enumerate(proposals):
        with open(f"new_proposals/proposal_{i}.json", "w") as f:
            json.dump(p, f, indent=2)

def build_turn_3():
    # 路径已由框架设定为 assets/data_round_01_aligned_mix_800_0167/turn_3
    os.makedirs("emergency_updates", exist_ok=True)
    
    # 模拟预算缩减：12000 * 0.8 = 9600
    # 此时 QT-Alpha (11500) 也不够了，原本符合条件的全灭
    # 引入新的微调参数
    updates = {
        "QT-Alpha_v2": {
            "price": 9500, # 降价了，但...
            "est_failure_rate": 0.055, # 失败：故障率刚过 5% 的红线
            "power_consumption": 142
        },
        "DC-Zero_v2": {
            "price": 7500,
            "est_failure_rate": 0.06, # 依然高故障率
            "power_consumption": 125
        }
    }
    
    with open("emergency_updates/spec_adjustments.json", "w") as f:
        json.dump(updates, f, indent=2)

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
