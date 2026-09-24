import os
import argparse
import json

def build_turn_1():
    # 初始环境：预算规则、供应商黑名单、海量报价单
    os.makedirs("club_files/inbox", exist_ok=True)
    
    # 学校预算限制文件
    budget_info = {
        "total_grant": 1200,
        "currency": "USD",
        "category": "Tech Arts 2024",
        "notes": "Do not exceed the limit. Blacklisted vendors: 'TrashHeap-Recycle', 'Shady-Pete-Electronics'."
    }
    with open("club_files/school_policy.json", "w") as f:
        json.dump(budget_info, f)

    # 供应商报价单 - 包含符合/不符合规则的各项
    proposals = [
        {"item": "IBM Model M Keyboard", "year": 1987, "price": 150, "currency": "USD", "weight_kg": 2.5, "condition": "Mint", "vendor": "RetroBits"},
        {"item": "Macintosh Plus (No Mouse)", "year": 1986, "price": 400, "currency": "USD", "weight_kg": 7.5, "condition": "Repairable", "vendor": "OldSchool_Cool"},
        {"item": "Commodore 64", "year": 1982, "price": 200, "currency": "USD", "weight_kg": 1.8, "condition": "Mint", "vendor": "TrashHeap-Recycle"}, # 黑名单
        {"item": "Sony Trinitron CRT PVM", "year": 1992, "price": 300, "currency": "USD", "weight_kg": 18.5, "condition": "Mint", "vendor": "Studio_Liquidation"}, # 潜在风险：CRT+超重
        {"item": "Intel 486 Processor (Framed)", "year": 1989, "price": 80, "currency": "USD", "weight_kg": 0.5, "condition": "Mint", "vendor": "RetroBits"},
        {"item": "Amiga 500", "year": 1987, "price": 450, "currency": "USD", "weight_kg": 3.1, "condition": "Mint", "vendor": "Euro_Vintage_Vault"}, # 欧元潜在冲突项
        {"item": "Windows 95 Sealed Box", "year": 1995, "price": 100, "currency": "USD", "weight_kg": 0.8, "condition": "Mint", "vendor": "OldSchool_Cool"}
    ]
    
    for i, p in enumerate(proposals):
        with open(f"club_files/inbox/proposal_{i}.json", "w") as f:
            json.dump(p, f)

def build_turn_2():
    # 模拟增量更新
    os.makedirs("club_files/updates", exist_ok=True)
    
    # 新的报价单，包含诱导项
    new_proposals = [
        {"item": "NeXT Station", "year": 1990, "price": 500, "currency": "USD", "weight_kg": 6.0, "condition": "Mint", "vendor": "Silicon_Valley_Museum"},
        {"item": "Voodoo 2 Graphics Card", "year": 1998, "price": 120, "currency": "USD", "weight_kg": 0.4, "condition": "Mint", "vendor": "RetroBits"} # 超过1995年限制
    ]
    
    for i, p in enumerate(new_proposals):
        with open(f"club_files/updates/new_proposal_{i}.json", "w") as f:
            json.dump(p, f)

def build_turn_3():
    # 第三轮不需要新建目录，但需要修改某些隐性逻辑（Agent需在Prompt中获知）
    # 仅仅是为了符合结构，创建一个标记文件
    with open("club_files/emergency_notice.txt", "w") as f:
        f.write("URGENT: CHECK CURRENCY AND BUDGET CUTS!")

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
