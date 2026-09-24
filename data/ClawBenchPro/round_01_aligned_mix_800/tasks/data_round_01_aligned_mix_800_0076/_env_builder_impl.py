import os
import argparse
import json
import random

def build_turn_1():
    # 创建目录结构
    os.makedirs("incoming_claims", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    
    # 城市差旅标准数据
    per_diem = {
        "San Francisco": 350,
        "Hanoi": 150,
        "London": 300,
        "Tokyo": 280,
        "Singapore": 260
    }
    with open("reference/per_diem_rates.json", "w") as f:
        json.dump(per_diem, f)

    # 生成第一轮数据：混合了合规与违规的数据
    claims = [
        ["Claim_ID", "Employee", "Amount", "Category", "City", "Notes"],
        ["C001", "Alex Smith", "5200", "Overseas Research", "Hanoi", "Purchase of server nodes, no SN provided"], # 违规：超5000且无SN
        ["C002", "Maria Garcia", "120", "Meal", "San Francisco", "Client dinner"], # 合规
        ["C003", "John Doe", "4500", "Device", "London", "Sensor Carrier (iPad Pro)"], # 违规：耐用品
        ["C004", "Alex Smith", "800", "Travel", "Hanoi", "Hotel for 4 nights"], # 违规：800/4=200 > 150
        ["C005", "Li Wei", "3000", "Overseas Research", "Singapore", "Field testing units, SN: TECH-9921"], # 合规
    ]
    
    with open("incoming_claims/q1_claims.csv", "w") as f:
        for row in claims:
            f.write(",".join(row) + "\n")

def build_turn_2():
    # 模拟 Turn 2 的增量环境
    os.makedirs("new_batch", exist_ok=True)
    
    # 新的申请数据，包含上一轮出现的 Alex Smith (累犯)
    # 引入供应商陷阱 Global Tech Logistics
    new_claims = [
        ["Claim_ID", "Employee", "Amount", "Category", "Vendor", "Notes"],
        ["C006", "Alex Smith", "45", "Gift", "Starbucks", "Holiday gift for client"], # 违规：高风险人员+礼品
        ["C007", "Li Wei", "1200", "Research", "Global Tech Logistics", "Cable wholesale"], # 违规：黑名单供应商
        ["C008", "Sarah Chen", "2500", "Device", "Best Buy", "Foldable screen test unit"], # 经理感兴趣的折叠屏
        ["C009", "Maria Garcia", "300", "Travel", "Hilton", "Stay in Tokyo"],
    ]
    
    with open("new_batch/q2_claims.csv", "w") as f:
        for row in new_claims:
            f.write(",".join(row) + "\n")

def build_turn_3():
    # Turn 3 主要是逻辑处理，不增加大规模新文件，但增加一个位置分布表
    os.makedirs("compliance_geo", exist_ok=True)
    geo_data = {
        "Alex Smith": "International",
        "Maria Garcia": "Domestic",
        "John Doe": "International",
        "Li Wei": "International",
        "Sarah Chen": "Domestic"
    }
    with open("compliance_geo/employee_locations.json", "w") as f:
        json.dump(geo_data, f)

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
