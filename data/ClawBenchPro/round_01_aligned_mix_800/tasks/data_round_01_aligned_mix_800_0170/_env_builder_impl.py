import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0170/turn_1
    os.makedirs("raw_proposals", exist_ok=True)
    os.makedirs("compliance", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 罚金公式
    with open("compliance/penalty_formula.txt", "w") as f:
        f.write("Penalty = (Maintenance_Hours - 48) * 150 + (Expected_Failure_Rate * 5000)\n")
        f.write("Note: Maintenance_Hours cannot exceed 72 hours.")

    # 2. ISO 认证零件清单
    with open("compliance/certified_parts.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Part_ID", "Material", "ISO_Certified"])
        writer.writerow(["P001", "Steel-Grade-A", "Yes"])
        writer.writerow(["P002", "Polymer-B", "Yes"])
        writer.writerow(["P003", "Lead-Alloy-X", "No"]) # 预埋陷阱
        writer.writerow(["P004", "PTFE-S", "Yes"]) # 第一轮合规，第二轮将被禁

    # 3. 供应商方案
    proposals = [
        {
            "vendor": "FastFix_Inc",
            "quote": 5000,
            "hours": 30,
            "failure_rate": 0.05,
            "parts": ["P001", "P002"]
        },
        {
            "vendor": "Cheap_Repair_Co",
            "quote": 3000,
            "hours": 70, # 接近 72 限制
            "failure_rate": 0.15, # 罚金会很高
            "parts": ["P001", "P003"] # 使用了非 ISO 零件，应被剔除
        },
        {
            "vendor": "EcoSystems_LTD",
            "quote": 5500,
            "hours": 40,
            "failure_rate": 0.02,
            "parts": ["P001", "P004"] # 包含 PTFE-S，第一轮的最优解候选，但第二轮会被禁
        }
    ]
    for p in proposals:
        with open(f"raw_proposals/{p['vendor']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0170/turn_2
    os.makedirs("updates/new_bids", exist_ok=True)
    
    # 1. 新禁令文件
    with open("updates/new_safety_ban.pdf.txt", "w") as f: # 简略模拟PDF
        f.write("URGENT SAFETY BULLETIN\n")
        f.write("Effective immediately: Any equipment containing 'PTFE-S' or 'Lead-Alloy' is banned due to toxic degradation.\n")
        f.write("Previous certifications for these materials are revoked.")

    # 2. 新增报价，其中一个看起来很诱人但价格略高
    new_bid = {
        "vendor": "Secure_Tech_Solutions",
        "quote": 6200,
        "hours": 36,
        "failure_rate": 0.01,
        "parts": ["P001", "P002"]
    }
    with open("updates/new_bids/Secure_Tech.json", "w") as f:
        json.dump(new_bid, f, indent=4)

def build_turn_3():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0170/turn_3
    os.makedirs("vendor_catalogs", exist_ok=True)
    
    # 提供模块化选项，用于应对预算削减
    # 只有通过分析这个文件，才能找到降低 FastFix 或 Secure_Tech 报价的方法
    catalog = {
        "FastFix_Inc": {
            "core_service": 4000,
            "extended_warranty_package": 1000,
            "failure_rate_if_core_only": 0.08
        },
        "Secure_Tech_Solutions": {
            "core_service": 5500,
            "calibration_audit_package": 700,
            "failure_rate_if_core_only": 0.02
        }
    }
    with open("vendor_catalogs/modular_pricing.json", "w") as f:
        json.dump(catalog, f, indent=4)

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
