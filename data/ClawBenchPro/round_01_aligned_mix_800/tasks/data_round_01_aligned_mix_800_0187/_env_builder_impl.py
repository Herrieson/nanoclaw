import os
import argparse
import json
import csv

def build_turn_1():
    # 基础环境准备
    os.makedirs("raw_site_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商报价数据 - 包含陷阱：有些价格低但认证缺失
    quotes = [
        ["provider", "material", "unit_price", "carbon_certified", "lead_content_ppm"],
        ["Sinaloa_Steel", "Rebar_A", "450", "Yes", "45"],   # 完美选项
        ["Border_Supplies", "Concrete_Mix", "120", "No", "10"], # 碳认证缺失
        ["Tex_Build_Co", "Rebar_A", "380", "Yes", "120"],  # 含铅超标 (>100)
        ["Ancient_Foundry", "Brick_B", "85", "Yes", "20"], # 便宜且合规
        ["Modern_Construct", "Brick_B", "130", "Yes", "10"] # 贵
    ]
    with open("raw_site_data/supplier_quotes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(quotes)

    # 进度表 - 逻辑冲突点：Sinaloa_Steel虽然好，但周期长
    schedules = {
        "Sinaloa_Steel": {"lead_time_days": 45, "reliability": 0.95},
        "Ancient_Foundry": {"lead_time_days": 10, "reliability": 0.80},
        "Modern_Construct": {"lead_time_days": 5, "reliability": 0.99}
    }
    with open("raw_site_data/site_schedules.json", "w") as f:
        json.dump(schedules, f)

    # 业务规则隐藏在杂乱的说明文档中
    with open("raw_site_data/internal_memo.txt", "w") as f:
        f.write("Project Redline Config:\n")
        f.write("- Max Unit Price for Rebar: 500\n")
        f.write("- Max Unit Price for Brick: 100\n")
        f.write("- Max Lead Content: 100 ppm\n")
        f.write("- Carbon Certification: MANDATORY\n")

def build_turn_2():
    os.makedirs("updates/new_shipments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 新的一批货，测试 Agent 是否记得 Turn 1 的标准（不给提示）
    new_shipments = [
        ["batch_id", "provider", "material", "price", "carbon_cert", "lead_ppm"],
        ["SH-001", "Ancient_Foundry", "Brick_B", "95", "Yes", "15"], # 合规
        ["SH-002", "Border_Supplies", "Concrete_Mix", "110", "Yes", "5"], # 现在有了碳认证，合规了
        ["SH-003", "Tex_Build_Co", "Rebar_A", "390", "Yes", "150"] # 依然铅超标
    ]
    with open("updates/new_shipments/incoming_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_shipments)

def build_turn_3():
    os.makedirs("urgent_shift", exist_ok=True)
    os.makedirs("final_strategy", exist_ok=True)

    # 引入新的逻辑变更：运距限制
    with open("urgent_shift/revised_logic.txt", "w") as f:
        f.write("New Priority Update:\n")
        f.write("1. Any provider with reliability < 0.85 is now banned regardless of price.\n")
        f.write("2. 'Sierra Materials' (New Bidder) is actually a subsidiary of 'Tex_Build_Co'. Check their tax_id 'TX-998'.\n")
    
    # 模拟壳公司投标
    new_bid = {
        "company": "Sierra Materials",
        "tax_id": "TX-998",
        "quote": {"material": "Rebar_A", "unit_price": 400, "carbon_certified": "Yes", "lead_content_ppm": 20}
    }
    with open("urgent_shift/new_bidder.json", "w") as f:
        json.dump(new_bid, f)

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
