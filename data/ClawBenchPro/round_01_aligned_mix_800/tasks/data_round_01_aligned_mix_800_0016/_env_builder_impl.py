import os
import argparse
import json
import random

def build_turn_1():
    # 临床数据模拟
    os.makedirs("raw_clinical_data", exist_ok=True)
    for i in range(1, 21):
        with open(f"raw_clinical_data/sample_{i:02d}.json", "w") as f:
            # 故意制造一些噪声数据
            data = {
                "sample_id": f"S-{1000+i}",
                "raw_value": round(random.uniform(50, 150), 2),
                "baseline": 40.0,
                "region_tag": "Type-A" if i % 3 != 0 else "Type-C",
                "biomarker_index": 0.0 # 待Agent根据公式计算
            }
            json.dump(data, f)

    # 协议文件
    os.makedirs("protocols", exist_ok=True)
    with open("protocols/calculation_standard.pdf.txt", "w") as f:
        f.write("Standard Protocol v1.1\n")
        f.write("Corrected Biomarker Formula: index = (raw_value - baseline) * 1.15 + log10(raw_value)\n")
        f.write("Selection Criterion: Top candidates must have index > 80.0\n")

    # 供应商数据
    os.makedirs("vendors", exist_ok=True)
    vendor_a = {
        "name": "Genex Corp",
        "base_price": 70000,
        "sequencing_runs": 2,
        "shipping_fee": 5000,
        "notes": "Premium quality, fixed cost."
    }
    vendor_b = {
        "name": "BioLogic Solutions",
        "base_price": 60000,
        "sequencing_runs": 2,
        "shipping_fee": 15000,
        "notes": "*Mandatory insurance fee of 12000 not included in base price."
    }
    vendor_c = {
        "name": "QuickSeq",
        "base_price": 50000,
        "sequencing_runs": 1,
        "upgrade_to_2_runs": 20000,
        "shipping_fee": 2000,
        "notes": "Low initial cost."
    }
    
    with open("vendors/proposals.json", "w") as f:
        json.dump([vendor_a, vendor_b, vendor_c], f, indent=4)

def build_turn_2():
    # 增加突发变动
    os.makedirs("vendors/updates", exist_ok=True)
    # 针对供应商A的涨价，迫使Agent重新评估
    with open("vendors/updates/notice_genex.txt", "w") as f:
        f.write("Due to logistics issues, Genex Corp's shipping fee is increased to 18000 effective immediately.")

def build_turn_3():
    # 模拟环境状态保持，不需要物理文件增加，更多是逻辑挑战
    # 但为了符合流程，我们增加一个财务部的官方通知
    os.makedirs("finance", exist_ok=True)
    with open("finance/budget_cut.txt", "w") as f:
        f.write("URGENT: Overall project budget reduced by 15% from the initial cap defined in Turn 1.")

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
