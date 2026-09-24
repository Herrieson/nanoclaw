import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录结构
    os.makedirs("cur_reports", exist_ok=True)
    os.makedirs("metrics", exist_ok=True)

    # 1. 构造混乱的 CSV 账单文件，列故意打乱顺序，且含有 JSON 格式的 tags
    # i-101: 极度昂贵，利用率极低 (僵尸)。包含 core_algo 标签 (Turn 2的陷阱)
    # i-102: 正常机器
    # i-103: 昂贵，利用率低 (僵尸)。无豁免标签。
    # vol-201: 未挂载，昂贵。包含重要数据 (Turn 3的陷阱)
    # vol-202: 已挂载，正常。
    # vol-203: 未挂载，便宜。
    csv_data = [
        ["Cost_HalfMonth", "Operation", "ResourceId", "Tags_JSON", "UsageType"],
        ["4000", "RunInstances", "i-101", '{"env":"dev", "project":"core_algo"}', "BoxUsage:p3.8xlarge"],
        ["500", "RunInstances", "i-102", '{"env":"prod", "team":"backend"}', "BoxUsage:g4dn.xlarge"],
        ["2000", "RunInstances", "i-103", '{"env":"test"}', "BoxUsage:p2.8xlarge"],
        ["600", "CreateVolume", "vol-201", '{"owner":"dba"}', "EBS:VolumeUsage.piops"],
        ["200", "CreateVolume", "vol-202", '{"env":"prod"}', "EBS:VolumeUsage.gp3"],
        ["250", "CreateVolume", "vol-203", '{}', "EBS:VolumeUsage.gp3"]
    ]
    
    with open("cur_reports/aws_billing_01.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. 构造 GPU 利用率 JSON
    gpu_metrics = {
        "i-101": {"avg_utilization": 2.1, "max_utilization": 18.0},
        "i-102": {"avg_utilization": 65.0, "max_utilization": 99.0},
        "i-103": {"avg_utilization": 1.5, "max_utilization": 4.5}
    }
    with open("metrics/gpu_metrics.json", "w") as f:
        json.dump(gpu_metrics, f, indent=4)

    # 3. 构造 EBS 挂载状态 CSV (又是另一种格式)
    ebs_status = [
        "VolumeId,AttachmentState",
        "vol-201,available",
        "vol-202,in-use",
        "vol-203,available"
    ]
    with open("metrics/ebs_status.csv", "w") as f:
        f.write("\n".join(ebs_status))


def build_turn_2():
    # 在已有环境增加豁免名单
    os.makedirs("compliance", exist_ok=True)
    with open("compliance/exceptions_list.txt", "w") as f:
        f.write("URGENT: Do NOT terminate any resource containing the following tags:\n")
        f.write("- project:core_algo\n")
        f.write("- env:prod\n")

    # 增加新的账单数据，列顺序再次不同
    # i-104: 僵尸，无豁免，会被回收。
    # i-105: 僵尸，有豁免，不能碰。
    csv_data_new = [
        ["Tags_JSON", "ResourceId", "Operation", "UsageType", "Cost_HalfMonth"],
        ['{"owner":"research"}', "i-104", "RunInstances", "BoxUsage:p2.xlarge", "500"],
        ['{"env":"prod"}', "i-105", "RunInstances", "BoxUsage:p3.2xlarge", "1000"]
    ]
    with open("cur_reports/aws_billing_update.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data_new)
        
    # 为新机器更新 metrics
    gpu_metrics_new = {
        "i-104": {"avg_utilization": 1.0, "max_utilization": 3.0},
        "i-105": {"avg_utilization": 0.5, "max_utilization": 1.0}
    }
    
    # 因为外层框架会在回合间保持文件，我们直接读取更新现有的 metrics 文件
    if os.path.exists("metrics/gpu_metrics.json"):
        with open("metrics/gpu_metrics.json", "r") as f:
            existing_metrics = json.load(f)
        existing_metrics.update(gpu_metrics_new)
        with open("metrics/gpu_metrics.json", "w") as f:
            json.dump(existing_metrics, f, indent=4)


def build_turn_3():
    # 注入数据安全委员会的快照元数据
    os.makedirs("security", exist_ok=True)
    snapshot_meta = {
        "critical_volumes_with_snapshots": [
            "vol-201",
            "vol-999" # 干扰项
        ]
    }
    with open("security/snapshot_metadata.json", "w") as f:
        json.dump(snapshot_meta, f, indent=4)


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
