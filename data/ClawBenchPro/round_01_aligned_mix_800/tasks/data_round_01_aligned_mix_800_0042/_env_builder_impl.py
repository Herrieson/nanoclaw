import os
import argparse
import json
import csv
import random

def build_turn_1():
    os.makedirs("evidence/raw_transfers", exist_ok=True)
    os.makedirs("configs", exist_ok=True)
    
    # 嫌疑人名单
    suspects = [
        {"id": "ACC_001", "name": "Seamus O'Malley", "type": "Individual"},
        {"id": "ACC_002", "name": "Emerald Horizon Ltd", "type": "Company"},
        {"id": "ACC_003", "name": "Blue Chip Holdings", "type": "Company"},
        {"id": "ACC_004", "name": "Shell Global", "type": "Company"}
    ]
    with open("configs/suspect_list.json", "w") as f:
        json.dump(suspects, f, indent=4)

    # 实体映射 (UBO 隐藏关系)
    # Shell Global -> Blue Chip -> Emerald Horizon (三层)
    with open("configs/entity_mapping.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["parent_entity", "child_entity", "ownership_pct"])
        writer.writerow(["Shell Global", "Blue Chip Holdings", 100])
        writer.writerow(["Blue Chip Holdings", "Emerald Horizon Ltd", 80])
        writer.writerow(["Seamus O'Malley", "Shell Global", 100])

    # 原始交易 (包含干扰项)
    transfers = [
        ["TRX_101", "ACC_001", "ACC_002", "48000", "USD", "Consulting"], # 低于50k
        ["TRX_102", "ACC_002", "ACC_003", "46000", "EUR", "Dividends"],  # 46000*1.1 = 50600, 触发红线
        ["TRX_103", "ACC_003", "ACC_004", "100000", "USD", "Acquisition"], # 触发红线且涉及三层架构
        ["TRX_104", "ACC_005", "ACC_006", "120000", "USD", "Normal Trade"], # 金额大但不在嫌疑名单
    ]
    with open("evidence/raw_transfers/logs_jan.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "from_acc", "to_acc", "amount", "currency", "memo"])
        writer.writerows(transfers)

def build_turn_2():
    os.makedirs("evidence/invoices", exist_ok=True)
    # 黑名单地区
    with open("evidence/restricted_jurisdictions.txt", "w") as f:
        f.write("Cayman Islands\nPanama\nLuxembourg")
    
    # 增量交易数据
    # 模拟循环转账的一部分，并且引入黑名单地域的小额交易
    updates = [
        ["TRX_201", "ACC_002", "ACC_001", "5000", "USD", "Refund", "Cayman Islands"], # 命中黑名单1
        ["TRX_202", "ACC_002", "ACC_005", "60000", "USD", "Art Purchase", "USA"],      # 金额虽大但有发票(待会生成)
        ["TRX_203", "ACC_001", "ACC_002", "2000", "EUR", "Misc", "Panama"]            # 命中黑名单2 -> 触发监控
    ]
    with open("evidence/batch_update_02.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "from_acc", "to_acc", "amount", "currency", "memo", "origin_country"])
        writer.writerows(updates)
        
    # 合法发票干扰项
    with open("evidence/invoices/INV_TRX_202.txt", "w") as f:
        f.write("Invoice for Oil Painting. Seller: Sotheby's. Amount: 60000 USD.")

def build_turn_3():
    os.makedirs("evidence/final_dump", exist_ok=True)
    # 最终审计数据，制造循环转账闭环
    # 之前的路径：ACC_001 -> ACC_002 (TRX_101), 此时增加 ACC_002 -> ACC_001 (TRX_301) 构成循环
    final_data = [
        ["TRX_301", "ACC_002", "ACC_001", "45000", "USD", "Stock Buyback"],
        ["TRX_302", "ACC_004", "ACC_001", "90000", "USD", "Liquidation"]
    ]
    with open("evidence/final_dump/audit_march.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "from_acc", "to_acc", "amount", "currency", "memo"])
        writer.writerows(final_data)

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
