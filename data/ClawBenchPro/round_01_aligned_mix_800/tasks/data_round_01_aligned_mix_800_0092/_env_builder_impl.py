import os
import argparse
import json
import csv

def build_turn_1():
    # 建立初始目录结构
    os.makedirs("archives/raw_metadata", exist_ok=True)
    os.makedirs("compliance_standards", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 数字化标准文件 (PDF/Markdown 模拟)
    with open("compliance_standards/preservation_protocol_v1.txt", "w") as f:
        f.write("Digitalization Protocol 2024:\n")
        f.write("- Condition score must be > 7 to survive standard scanning.\n")
        f.write("- Books printed before 1850 require 'Ultra-Gentle' mode (Cost x 2.5).\n")
        f.write("- Maximum budget for Phase 1: $15,000.\n")
        f.write("- Items with 'Restricted' status cannot be sent to third-party labs.\n")

    # 2. 初始藏书清单 (CSV)
    books = [
        ["ID", "Title", "Year", "Condition_Score", "Status", "Estimated_Pages"],
        ["B001", "The History of Texas Schools", "1845", "9", "Available", "320"], # Pre-1850, Expensive
        ["B002", "Common Flora of the Midwest", "1880", "5", "Available", "150"], # Condition < 7, Needs special care
        ["B003", "Library Governance Manual", "1920", "8", "Restricted", "200"],  # Restricted
        ["B004", "Early Polish Immigrants in TX", "1895", "10", "Available", "500"], # Safe
        ["B005", "Agricultural Records Vol I", "1830", "4", "Available", "100"],   # Pre-1850 AND low condition
        ["B006", "Local Poet Anthology", "1950", "9", "Available", "120"],       # Standard
    ]
    with open("archives/raw_metadata/initial_batch.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(books)

    # 3. 供应商价格表
    vendor_rates = {
        "standard_per_page": 0.50,
        "ultra_gentle_surcharge_multiplier": 2.5,
        "manual_restoration_flat_fee": 500
    }
    with open("archives/raw_metadata/vendor_rates.json", "w") as f:
        json.dump(vendor_rates, f)

def build_turn_2():
    # 模拟收到一封紧急邮件的补丁数据
    os.makedirs("incoming", exist_ok=True)
    with open("incoming/policy_update.txt", "w") as f:
        f.write("URGENT: School board updated the Digitization Safety Act.\n")
        f.write("Effective immediately: Condition Score threshold raised to 8.\n")
        f.write("New restriction: Any book containing 'Agricultural' data must be marked 'Restricted' for privacy review.\n")

def build_turn_3():
    # 模拟最后一轮的突发情况：第三方实验室倒闭，Restricted 规则影响扩大
    with open("incoming/vendor_alert.txt", "w") as f:
        f.write("Alert: Our primary third-party lab 'ScanMaster' is no longer accepting 'High-Value' items (Year < 1860).\n")
        f.write("All such items must now be processed in-house at a 30% higher cost than the previous ultra-gentle rate.\n")

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
