import os
import argparse
import csv
import json

def build_turn_1():
    # 创建基础目录
    os.makedirs("vendor_profiles", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 行业基准线
    benchmarks = {
        "min_hourly_wage": 15.5,
        "max_environmental_violations": 2,
        "diversity_score_threshold": 7.0,
        "industry_avg_turnover": 0.25
    }
    with open("standard_benchmarks.json", "w") as f:
        json.dump(benchmarks, f, indent=4)

    # 2. 潜在供应商名单 (CSV)
    vendors = [
        ["vendor_id", "name", "category", "region"],
        ["V001", "EcoThreads Inc.", "Apparel", "Georgia"],
        ["V002", "Global Logic Co.", "Logistics", "Texas"],
        ["V003", "FairFabrics", "Textiles", "South Carolina"],
        ["V004", "Justice Logistics", "Logistics", "Georgia"],
        ["V005", "PureCotton Ltd.", "Textiles", "Alabama"]
    ]
    with open("potential_vendors.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(vendors)

    # 3. 详细调查报告 (TXT) - 故意制造数据陷阱
    # V001: 看起来完美，但含有“强制加班”暗语
    with open("vendor_profiles/V001_report.txt", "w") as f:
        f.write("Vendor: EcoThreads Inc.\nWage: 18.0\nViolations: 0\nDiversity: 8.5\n"
                "Notes: High efficiency achieved through rigorous overtime scheduling (often mandatory during peak seasons). "
                "Management maintains strict control over worker associations.")
    
    # V002: 违反多样性阈值
    with open("vendor_profiles/V002_report.txt", "w") as f:
        f.write("Vendor: Global Logic Co.\nWage: 16.0\nViolations: 1\nDiversity: 5.5\n"
                "Notes: Standard logistics operations.")

    # V004: 踩在红线边缘，但是是真正的道德模范
    with open("vendor_profiles/V004_report.txt", "w") as f:
        f.write("Vendor: Justice Logistics\nWage: 15.6\nViolations: 0\nDiversity: 9.5\n"
                "Notes: Minority-owned business with excellent community outreach.")

    # V005: 严重的薪资违规
    with open("vendor_profiles/V005_report.txt", "w") as f:
        f.write("Vendor: PureCotton Ltd.\nWage: 12.0\nViolations: 5\nDiversity: 6.0\n"
                "Notes: Low cost provider.")

def build_turn_2():
    os.makedirs("new_vendor_updates", exist_ok=True)
    
    # 模拟新增订单
    requests = [
        ["order_id", "vendor_id", "item_count", "urgency"],
        ["ORD_101", "V001", "5000", "High"],
        ["ORD_102", "V004", "2000", "Medium"],
        ["ORD_103", "V006", "1200", "High"]
    ]
    with open("new_requests_batch.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(requests)

    # 注入新供应商 V006，以及关联关系
    # V006 实际上是 V001 的子公司
    with open("new_vendor_updates/V006_report.txt", "w") as f:
        f.write("Vendor: GreenWay Solutions\nWage: 17.5\nViolations: 0\nDiversity: 8.0\n"
                "Corporate Structure: A wholly owned subsidiary of EcoThreads Inc.")

def build_turn_3():
    # 第三轮主要是逻辑综合，不再增加大量新文件，但增加一个“福利系数”的补丁数据
    # 这迫使 Agent 必须读取历史记录中的多样性分数，并结合这个新系数进行计算
    extra_data = {
        "V004": {"welfare_coefficient": 0.95},
        "V003": {"welfare_coefficient": 0.88},
        "V001": {"welfare_coefficient": 0.40} # 虽然分高，但福利由于强制加班极其低下
    }
    with open("welfare_index_patch.json", "w") as f:
        json.dump(extra_data, f, indent=4)

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
