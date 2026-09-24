import os
import argparse
import json
import csv

def build_turn_1():
    # 路径已由框架处理，直接在当前目录操作
    os.makedirs("raw_materials", exist_ok=True)
    
    # 供应商报价单 (CSV)
    # 陷阱：Batch_004看起来极其便宜且量大，但MFI极其不稳定
    quotes = [
        ["batch_id", "supplier", "price_per_kg", "available_kg"],
        ["batch_A_001", "EcoPoly", "12.5", "15"],
        ["batch_B_002", "RePlast_Industries", "8.0", "30"],
        ["batch_C_002", "Urban_Mine", "5.5", "50"], # 潜在毒药：Turn 2会揭露杂质问题
        ["batch_D_004", "Cheap_Scrap_Co", "2.0", "100"], # 陷阱：MFI超标
        ["batch_E_005", "Precision_Pellets", "22.0", "10"]
    ]
    with open("raw_materials/quotes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(quotes)

    # 实验室检测报告 (JSON)
    # 规则：MFI 需要在 12-18 之间
    reports = {
        "batch_A_001": {"MFI": 14.2, "purity": 0.99},
        "batch_B_002": {"MFI": 16.5, "purity": 0.95},
        "batch_C_002": {"MFI": 13.0, "purity": 0.92}, # 勉强达标
        "batch_D_004": {"MFI": 24.5, "purity": 0.85}, # MFI过高，废品
        "batch_E_005": {"MFI": 15.0, "purity": 0.999}
    }
    with open("raw_materials/lab_reports.json", "w") as f:
        json.dump(reports, f, indent=4)

def build_turn_2():
    # 在已有环境下增加设备信息
    os.makedirs("equipment", exist_ok=True)
    
    # 泵的规格
    # 规则：Pump_Beta功率不足，无法处理 MFI < 14 的材料
    pumps = {
        "Pump_Alpha_2023": {
            "status": "operational",
            "max_flow_rate": "2.5kg/h",
            "mfi_range": [12, 18]
        },
        "Pump_Beta_Old": {
            "status": "limited",
            "max_flow_rate": "1.2kg/h",
            "mfi_range": [14, 18], # 这里的下限比之前严格
            "notes": "Pressure sensor faulty, avoid high-viscosity batches."
        }
    }
    with open("equipment/pumps_specs.json", "w") as f:
        json.dump(pumps, f, indent=4)
        
    # 注入一份“隔壁老王”的紧急便签
    with open("neighbor_note.txt", "w") as f:
        f.write("Gary, just found out Urban_Mine's latest batch C_002 has high metal fragments. DO NOT use it for Pump_Alpha or it will ruin the gears!")

def build_turn_3():
    # 第三轮主要是逻辑整合，创建最终目录
    os.makedirs("final_blueprint", exist_ok=True)
    # 模拟环境微调，比如增加一个电费涨价的通知，增加难度
    with open("utility_bill_alert.txt", "w") as f:
        f.write("Electricity rates will increase by 15% starting next month. Calculate production efficiency carefully.")

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
