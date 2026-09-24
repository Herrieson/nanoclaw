import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("aws_billing", exist_ok=True)
    os.makedirs("tagging_policies", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 构造极具迷惑性的标签树，嵌套字典与列表
    aws_policy = {
        "mandatory_tags": ["department", "cost_center"],
        "allowed_values": {
            "department": ["Engineering", "AI-Research", "Marketing", "Data"],
            "cost_center": {
                "Engineering": ["E-10", "E-11"],
                "AI-Research": ["AI-99"],
                "Marketing": ["M-01"],
                "Data": ["D-50"]
            }
        }
    }
    with open("tagging_policies/aws_policy.json", "w") as f:
        json.dump(aws_policy, f)
        
    # AWS EBS 账单：设置边缘值陷阱
    with open("aws_billing/ebs_usage.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["volume_id", "status", "avg_iops_30d", "avg_throughput_30d", "monthly_cost"])
        writer.writerow(["vol-001", "available", 0, 0, 120.50]) # waste
        writer.writerow(["vol-002", "in-use", 0, 0, 55.00])     # waste
        writer.writerow(["vol-003", "in-use", 0, 0.1, 80.00])   # not waste (throughput not 0)
        writer.writerow(["vol-004", "in-use", 100, 50, 200.00]) # not waste
        writer.writerow(["vol-005", "available", 5, 0, 150.00]) # waste (available dominates iops)
        
    # AWS GPU 账单：设置 < 15% 与 <=40% 的数值陷阱
    with open("aws_billing/ec2_gpu_metrics.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["instance_id", "instance_type", "avg_gpu_util_30d", "max_gpu_util_30d", "monthly_cost"])
        writer.writerow(["i-g001", "p3.2xlarge", 12.5, 35.0, 1500.00])  # waste
        writer.writerow(["i-g002", "g4dn.xlarge", 14.9, 40.1, 400.00])  # not waste (max > 40)
        writer.writerow(["i-g003", "p3.8xlarge", 15.0, 30.0, 6000.00])  # not waste (avg >= 15)
        writer.writerow(["i-g004", "g4dn.2xlarge", 5.0, 25.0, 800.00])  # waste
        writer.writerow(["i-m001", "m5.large", 2.0, 10.0, 100.00])      # not waste (not a target gpu type)
        
    # 复杂的资源标签映射
    tags = {
        "vol-001": {"tags": {"department": "Engineering", "cost_center": "E-10"}}, # valid
        "vol-002": {"tags": {"department": "AI-Research", "cost_center": "E-10"}}, # invalid CC (AI-99 expected)
        "vol-005": {"tags": {"department": "Data", "cost_center": "D-50"}},        # valid
        "i-g001": {"tags": {"department": "Marketing", "cost_center": "M-01"}},    # valid
        "i-g004": {"tags": {"department": "Engineering"}}                          # invalid (missing mandatory tag)
    }
    with open("aws_billing/resource_tags.json", "w") as f:
        json.dump(tags, f)

def build_turn_2():
    # 增量 GCP 数据，以及状态修正文件
    os.makedirs("gcp_billing", exist_ok=True)
    os.makedirs("updates", exist_ok=True)
    
    gcp_policy = {
         "mandatory_tags": ["dept", "project"],
         "allowed_values": {
             "dept": ["Eng", "AI", "Mkt", "Data"],
             "project": {"Eng": ["P-1", "P-2"], "AI": ["P-X"]}
         }
    }
    with open("tagging_policies/gcp_policy.json", "w") as f:
        json.dump(gcp_policy, f)
        
    # GCP disks - 字段变化挑战
    with open("gcp_billing/gcp_disks.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["disk_id", "disk_state", "read_bytes_30d", "write_bytes_30d", "monthly_cost"])
        writer.writerow(["disk-101", "UNATTACHED", 0, 0, 85.00])     # waste
        writer.writerow(["disk-102", "ATTACHED", 0, 0, 45.00])       # waste
        writer.writerow(["disk-103", "ATTACHED", 1024, 0, 90.00])    # not waste
        
    # GCP compute - 结构变化挑战
    compute_metrics = [
        {"vm_id": "vm-g1", "machine_type": "a2-highgpu-1g", "metrics": {"avg_util": 8.0, "peak_util": 20.0}, "monthly_cost": 2000.00}, # waste
        {"vm_id": "vm-g2", "machine_type": "a2-highgpu-2g", "metrics": {"avg_util": 16.0, "peak_util": 35.0}, "monthly_cost": 4000.00} # not waste
    ]
    with open("gcp_billing/gcp_compute_metrics.json", "w") as f:
        json.dump(compute_metrics, f)
        
    # GCP tags
    with open("gcp_billing/gcp_tags.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["resource_id", "dept", "project"])
        writer.writerow(["disk-101", "Eng", "P-1"])
        writer.writerow(["disk-102", "AI", "P-X"])
        writer.writerow(["vm-g1", "Data", "P-1"]) # invalid project
        
    # 部门豁免列表
    with open("updates/exemption_list.txt", "w") as f:
        f.write("AI-Research\nAI\n")

def build_turn_3():
    # 第三轮：财务阻击战与冲突约束
    os.makedirs("finance", exist_ok=True)
    os.makedirs("resource_metadata", exist_ok=True)
    
    with open("finance/discount_rates.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["department_alias", "required_savings_percentage"])
        writer.writerow(["Engineering", 0.5])
        writer.writerow(["Eng", 0.5])
        writer.writerow(["Marketing", 1.0])
        writer.writerow(["Mkt", 1.0])
        writer.writerow(["Data", 0.8])
    
    # 引发冲突的关键业务标记，强制 Agent 放弃最顺手的操作
    critical_flags = {
        "vol-001": True,    # waste, should DELETE but critical -> NONE
        "disk-101": False,
        "i-g001": True,     # waste, should SPOT but critical -> NONE
        "vm-g1": False,
        "vol-005": False,
        "i-g004": False
    }
    with open("resource_metadata/critical_flags.json", "w") as f:
        json.dump(critical_flags, f)

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
