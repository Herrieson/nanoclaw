import os
import argparse
import csv
import json

def build_turn_1():
    # 媒体投放日志
    os.makedirs("media_logs", exist_ok=True)
    logs = [
        ["id", "vendor", "spend", "clicks", "conversions", "revenue", "tags"],
        ["L001", "VibeStream", "4800", "1200", "50", "6000", "Indie, Pop"], # ROI 1.25, CPC 4.0, Spend < 5000 (Penalty risk)
        ["L002", "RetroAd", "6000", "2000", "80", "6500", "Rock, Classic"], # ROI 1.08 (Risk), CPC 3.0
        ["L003", "JazzFly", "3000", "500", "20", "4000", "Jazz, Blues"],    # ROI 1.33, CPC 6.0 (Risk)
        ["L004", "TrendSet", "7000", "1500", "100", "9000", "Pop, Electronic"] # OK
    ]
    with open("media_logs/july_dump.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(logs)

    # 财务原始账单（故意制造轻微数据冲突）
    os.makedirs("raw_billing", exist_ok=True)
    billing = {
        "VibeStream": {"billed_amount": 4800, "contract_id": "VS-99"},
        "RetroAd": {"billed_amount": 6000, "contract_id": "RA-42"},
        "JazzFly": {"billed_amount": 3100, "contract_id": "JF-07"}, # Conflict with logs (3000 vs 3100)
        "TrendSet": {"billed_amount": 7000, "contract_id": "TS-11"}
    }
    with open("raw_billing/invoice_details.json", "w") as f:
        json.dump(billing, f)

def build_turn_2():
    # 模拟 turn_2 注入新方案
    os.makedirs("new_vendors", exist_ok=True)
    # 方案 A: 看起来很贵但 ROI 潜力大，风格摇滚
    with open("new_vendors/proposal_alpha.txt", "w") as f:
        f.write("Vendor: RockSolid\nExpected Spend: 8000\nTarget CPC: 3.8\nTags: Classic Rock, Heavy Metal\nProjected ROI: 1.5")
    
    # 方案 B: 风格 Indie (会被 turn 2 逻辑杀掉)
    with open("new_vendors/proposal_beta.txt", "w") as f:
        f.write("Vendor: IndieGo\nExpected Spend: 4000\nTarget CPC: 2.5\nTags: Indie, Alternative\nProjected ROI: 1.8")
    
    # 方案 C: 踩了 CPC 红线 (6.0 > 4.5)
    with open("new_vendors/proposal_gamma.txt", "w") as f:
        f.write("Vendor: PopBurst\nExpected Spend: 5500\nTarget CPC: 6.0\nTags: Rock, Pop\nProjected ROI: 2.1")

def build_turn_3():
    # Turn 3 主要是逻辑冲突和预算削减，不需要额外大量文件，
    # 仅注入一份全公司通用的“预算削减声明”作为干扰/背景
    with open("memo_internal.txt", "w") as f:
        f.write("To all departments: Immediate 20% cut on all projected vendor spendings starting next month.")

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
