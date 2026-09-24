import os
import json
import csv
import argparse

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def build_turn_1():
    ensure_dir("raw_data/billing")
    ensure_dir("raw_data/metrics")
    ensure_dir("policies")
    ensure_dir("deliverables")

    # 1. 部门标签映射
    tag_mapping = {
        "nlp-engine": "DataScience",
        "vision-api": "DataScience",
        "ui-v2": "R&D",
        "backend-core": "R&D",
        "ledger-db": "Finance",
        "payroll": "Finance",
        "ad-serving": "Marketing",
        "crm-sys": "Marketing"
    }
    with open("policies/tag_mapping.json", "w") as f:
        json.dump(tag_mapping, f, indent=4)

    # 2. 账单数据 (us-east-1)
    billing_data = [
        {"ResourceID": "i-gpu-ds-01", "ResourceType": "p3.2xlarge", "MonthlyCost": "3800.0", "Tag_Project": "nlp-engine"},
        {"ResourceID": "i-gpu-rd-01", "ResourceType": "g4dn.xlarge", "MonthlyCost": "1200.0", "Tag_Project": "ui-v2"}, # 陷阱：Turn 2 必须被移除
        {"ResourceID": "i-gpu-fin-01", "ResourceType": "p4d.24xlarge", "MonthlyCost": "32000.0", "Tag_Project": "ledger-db"}, # 陷阱：Turn 1 规则不包含Finance的GPU
        {"ResourceID": "i-gpu-mkt-01", "ResourceType": "g5.2xlarge", "MonthlyCost": "2500.0", "Tag_Project": "ad-serving"},
        {"ResourceID": "vol-ebs-ds-01", "ResourceType": "gp3", "MonthlyCost": "120.0", "Tag_Project": "vision-api"},
        {"ResourceID": "vol-ebs-rd-01", "ResourceType": "io2", "MonthlyCost": "800.0", "Tag_Project": "backend-core"},
        {"ResourceID": "vol-ebs-fin-01", "ResourceType": "gp2", "MonthlyCost": "350.0", "Tag_Project": "payroll"}, # 陷阱：Finance的EBS不能碰
    ]
    with open("raw_data/billing/us_east.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ResourceID", "ResourceType", "MonthlyCost", "Tag_Project"])
        writer.writeheader()
        writer.writerows(billing_data)

    # 3. GPU 指标
    gpu_metrics = {
        "i-gpu-ds-01": 8.5,    # 满足 < 15
        "i-gpu-rd-01": 4.2,    # 满足 < 15
        "i-gpu-fin-01": 2.1,   # 满足利用率，但部门不符
        "i-gpu-mkt-01": 11.0   # 满足利用率，但部门不符
    }
    with open("raw_data/metrics/us_gpu_metrics.json", "w") as f:
        json.dump(gpu_metrics, f, indent=4)

    # 4. EBS 指标
    ebs_metrics = {
        "vol-ebs-ds-01": 15,   # 满足 < 50
        "vol-ebs-rd-01": 120,  # > 50, 安全
        "vol-ebs-fin-01": 5    # 满足，但属于Finance，安全
    }
    with open("raw_data/metrics/us_ebs_metrics.json", "w") as f:
        json.dump(ebs_metrics, f, indent=4)

def build_turn_2():
    ensure_dir("raw_data/eu_region")

    # 欧洲区账单数据
    eu_billing_data = [
        {"ResourceID": "i-gpu-eu-ds-01", "ResourceType": "p3.2xlarge", "MonthlyCost": "4000.0", "Tag_Project": "vision-api"},
        {"ResourceID": "i-gpu-eu-rd-01", "ResourceType": "g4dn.xlarge", "MonthlyCost": "1300.0", "Tag_Project": "backend-core"},
        {"ResourceID": "vol-ebs-eu-mkt-01", "ResourceType": "gp3", "MonthlyCost": "200.0", "Tag_Project": "crm-sys"},
        {"ResourceID": "vol-ebs-eu-fin-01", "ResourceType": "io2", "MonthlyCost": "1000.0", "Tag_Project": "ledger-db"}
    ]
    with open("raw_data/eu_region/eu_billing.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ResourceID", "ResourceType", "MonthlyCost", "Tag_Project"])
        writer.writeheader()
        writer.writerows(eu_billing_data)

    # 欧洲区监控指标
    eu_metrics = {
        "gpu_utilization": {
            "i-gpu-eu-ds-01": 12.0, # 满足 < 15, DataScience
            "i-gpu-eu-rd-01": 6.0   # 满足 < 15, R&D 但在 Turn 2 新规中已免死
        },
        "ebs_iops": {
            "vol-ebs-eu-mkt-01": 10, # 满足 < 50, Marketing, 应该清理
            "vol-ebs-eu-fin-01": 0   # 满足 < 50, 但 Finance 免死
        }
    }
    with open("raw_data/eu_region/eu_metrics.json", "w") as f:
        json.dump(eu_metrics, f, indent=4)

def build_turn_3():
    ensure_dir("policies")
    # Spot 实例价格表 (按月计算)
    spot_pricing = {
        "p3.2xlarge": 1200.0,
        "g4dn.xlarge": 350.0,
        "p4d.24xlarge": 11000.0,
        "g5.2xlarge": 800.0
    }
    with open("policies/spot_pricing.json", "w") as f:
        json.dump(spot_pricing, f, indent=4)

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
