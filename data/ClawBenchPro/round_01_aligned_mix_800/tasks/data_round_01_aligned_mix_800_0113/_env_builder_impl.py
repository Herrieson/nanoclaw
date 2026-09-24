import os
import argparse
import json
import random

def build_turn_1():
    # 财务账目与供应商初步筛选
    os.makedirs("ledger", exist_ok=True)
    os.makedirs("compliance_docs", exist_ok=True)
    
    # 账目数据：包含逻辑矛盾和脏数据
    transactions = [
        {"id": "TXN_001", "vendor": "GlobalVax", "amount": 1250000, "category": "Vaccines", "date": "2023-11-15", "status": "Pending"},
        {"id": "TXN_002", "vendor": "BioCure_Ltd", "amount": 890000, "category": "Antibiotics", "date": "2023-11-16", "status": "Paid"},
        {"id": "TXN_003", "vendor": "MediSource", "amount": 450000, "category": "Equipment", "date": "2023-11-18", "status": "Paid"},
        {"id": "TXN_004", "vendor": "GlobalVax", "amount": 1250000, "category": "Vaccines", "date": "2023-11-15", "status": "Paid"}, # 重复交易
        {"id": "TXN_005", "vendor": "SwissPharma_SA", "amount": 2100000, "category": "Oncology", "date": "2023-11-20", "status": "Paid"},
    ]
    with open("ledger/q4_transactions.json", "w") as f:
        json.dump(transactions, f, indent=4)

    # 合规文件：包含各供应商的执照过期时间和所在国家
    compliance_rules = {
        "GlobalVax": {"country": "India", "license_expiry": "2024-12-31", "rating": "A"},
        "BioCure_Ltd": {"country": "Vietnam", "license_expiry": "2023-10-01", "rating": "B"}, # 已过期
        "MediSource": {"country": "USA", "license_expiry": "2025-05-20", "rating": "C"},
        "SwissPharma_SA": {"country": "Switzerland", "license_expiry": "2026-01-01", "rating": "A+"}
    }
    with open("compliance_docs/vendor_registry.json", "w") as f:
        json.dump(compliance_rules, f, indent=4)

def build_turn_2():
    # 模拟法规变更：由于地缘政治，部分国家被列入观察名单，审计标准提高
    os.makedirs("new_directives", exist_ok=True)
    directives = [
        "Directive 2024-A: All transactions from vendors in SE Asia (including Vietnam) require a mandatory 15% surcharge for insurance.",
        "Directive 2024-B: Indian vendors must provide a 'Quality Integrity Certificate' for any transaction exceeding $1M.",
        "Urgent: SwissPharma_SA has changed their banking route. All previous wire instructions are void."
    ]
    with open("new_directives/december_update.txt", "w") as f:
        f.write("\n".join(directives))

def build_turn_3():
    # 突发审计：要求对历史异常进行解释
    os.makedirs("audit_request", exist_ok=True)
    with open("audit_request/internal_query.txt", "w") as f:
        f.write("The internal board noticed a discrepancy in the oncology procurement. Please analyze why the SwissPharma deal total cost differs from our standard markup model (1.2x). Also, re-evaluate all India-based transactions based on the latest certificate status.")
    
    # 增加一个缺失的证书文件作为干扰项
    os.makedirs("vault", exist_ok=True)
    with open("vault/globalvax_integrity_cert.txt", "w") as f:
        f.write("Certificate Type: Quality Integrity\nVendor: GlobalVax\nStatus: EXPIRED on 2023-11-01")

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
