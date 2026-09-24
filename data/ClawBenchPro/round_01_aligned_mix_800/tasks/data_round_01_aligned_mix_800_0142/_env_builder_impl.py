import os
import argparse
import json
import csv

def build_turn_1():
    # 建立初始目录
    os.makedirs("inventory_logs", exist_ok=True)
    os.makedirs("standards", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商分级数据
    tiers = {
        "PharmaCorp": {"tier": 1, "reliability": 0.98},
        "MediQuick": {"tier": 2, "reliability": 0.85},
        "BioGlobal": {"tier": 1, "reliability": 0.95},
        "CheapMeds": {"tier": 3, "reliability": 0.60}
    }
    with open("standards/supplier_tiers.json", "w") as f:
        json.dump(tiers, f)

    # 内部政策 (模拟PDF文本)
    with open("standards/internal_policy.pdf", "w") as f:
        f.write("OFFICIAL POLICY: Schedule II drugs must ONLY be sourced from Tier 1.\n")
        f.write("THRESHOLD: If inventory turnover is below 0.2 units/day, re-evaluate supplier.\n")
        f.write("SAFETY_STOCK: Minimum 50 units for any pediatric antibiotic.")

    # 原始库存日志 - 包含脏数据和合规陷阱
    log_data = [
        ["timestamp", "drug_name", "batch_id", "supplier", "quantity", "schedule", "expiry_date"],
        ["2023-10-01", "Amoxicillin", "AMX-001", "PharmaCorp", "100", "III", "2024-12-01"],
        ["2023-10-01", "Oxycodone", "OXY-999", "MediQuick", "50", "II", "2025-01-01"], # 违规：Tier 2 供应 Schedule II
        ["2023-10-02", "Fentanyl", "FEN-123", "BioGlobal", "20", "II", "2023-11-15"], # 临期陷阱
        ["2023-10-02", "Amoxicillin", "AMX-002", "CheapMeds", "200", "III", "2024-05-01"],
        ["2023-10-03", "QC_FAIL_99", "ERR-404", "Unknown", "0", "N/A", "N/A"] # 垃圾数据
    ]
    with open("inventory_logs/weekly_intake.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log_data)

def build_turn_2():
    os.makedirs("emergency_updates", exist_ok=True)
    # 紧急更新：供应商降级与新限制
    # 故意不提具体数值，只给数据文件
    with open("emergency_updates/new_restricted_list.csv", "w") as f:
        f.write("supplier,status,new_limit\n")
        f.write("PharmaCorp,UNDER_INVESTIGATION,10\n") # 原本的Tier 1 受到限制
        f.write("BioGlobal,ACTIVE,100\n")

def build_turn_3():
    # 儿科需求激增数据
    surge_data = {
        "Amoxicillin": {"requested": 500, "priority": "CRITICAL"},
        "Oxycodone": {"requested": 10, "priority": "LOW"}
    }
    with open("emergency_updates/pediatric_surge.json", "w") as f:
        json.dump(surge_data, f)
    
    # 紧急豁免协议
    with open("standards/emergency_protocol.txt", "w") as f:
        f.write("EMERGENCY PROTOCOL v2.1\n")
        f.write("During surge: Purity standards can be lowered to 92.5%.\n")
        f.write("Exempt batches: Any batch from MediQuick is allowed for Amoxicillin regardless of Tier.")

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
