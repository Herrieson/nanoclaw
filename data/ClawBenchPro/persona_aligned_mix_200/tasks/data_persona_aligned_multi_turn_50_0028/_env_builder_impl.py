import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("raw_data/us_east/cloudtrail_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. EC2 Inventory US
    ec2_us = [
        # 陷阱1：GPU，无CostCenter，但日志里有活跃记录 -> 不符合闲置
        {
            "InstanceId": "i-0a1b2c3d4e5f60001",
            "InstanceType": "p3.2xlarge",
            "LaunchTime": "2023-10-01T08:00:00Z",
            "Tags": [{"Key": "Project", "Value": "AI-Research"}]
        },
        # 目标1：GPU，无CostCenter，无日志记录 -> 应该被抓出
        {
            "InstanceId": "i-0a1b2c3d4e5f60002",
            "InstanceType": "g4dn.xlarge",
            "LaunchTime": "2023-10-10T12:00:00Z",
            "Tags": [{"Key": "Owner", "Value": "Dev"}]
        },
        # 陷阱2：GPU，有CostCenter，无日志记录 -> 标签合规，不管
        {
            "InstanceId": "i-0a1b2c3d4e5f60003",
            "InstanceType": "p4d.24xlarge",
            "LaunchTime": "2023-10-15T00:00:00Z",
            "Tags": [{"Key": "CostCenter", "Value": "CC-992"}, {"Key": "Project", "Value": "Core"}]
        },
        # 陷阱3：非GPU，无CostCenter，无日志记录 -> 非目标机型
        {
            "InstanceId": "i-0a1b2c3d4e5f60004",
            "InstanceType": "m5.large",
            "LaunchTime": "2023-10-20T10:00:00Z",
            "Tags": []
        },
        # 目标2：GPU，无CostCenter，无活跃日志记录 -> 应该被抓出
        {
            "InstanceId": "i-0a1b2c3d4e5f60005",
            "InstanceType": "g5.12xlarge",
            "LaunchTime": "2023-10-05T09:30:00Z",
            "Tags": [{"Key": "Env", "Value": "Test"}]
        }
    ]
    with open("raw_data/us_east/ec2_inventory.json", "w") as f:
        json.dump({"Reservations": [{"Instances": ec2_us}]}, f, indent=2)

    # 2. CloudTrail Logs US (模拟深层嵌套结构)
    log_data_1 = {
        "Records": [
            {
                "eventTime": "2023-10-25T14:30:00Z",
                "eventName": "StartInstances",
                "responseElements": {
                    "instancesSet": {
                        "items": [
                            {"instanceId": "i-0a1b2c3d4e5f60001"}
                        ]
                    }
                }
            },
            {
                "eventTime": "2023-10-26T09:15:00Z",
                "eventName": "DescribeInstances",
                "requestParameters": {
                    "instancesSet": {
                        "items": [
                            {"instanceId": "i-0a1b2c3d4e5f60002"}
                        ]
                    }
                }
            }
        ]
    }
    with open("raw_data/us_east/cloudtrail_logs/log_001.json", "w") as f:
        json.dump(log_data_1, f, indent=2)

def build_turn_2():
    # 假设此时 Agent 已经保存了昨天的规则记录和US名单
    os.makedirs("raw_data/eu_central/cloudtrail_logs", exist_ok=True)
    
    # 1. 安全部门备忘录
    security_memo = """
SECURITY EXEMPTION MEMO - URGENT
Date: 2023-10-28
To: FinOps & Cloud Operations

The SecOps team has identified that certain highly sensitive instances are being flagged by automated scripts.
Effective immediately, any instance carrying the tag `SecurityLevel` with the value `High` MUST NOT be terminated, regardless of cost center compliance or inactivity. 
HOWEVER, this exemption is ONLY valid if the instance also has an `ApprovedBy` tag present (any value is acceptable, as long as the tag exists). If it has `SecurityLevel: High` but is missing `ApprovedBy`, it is considered a rogue deployment and should be handled by your normal termination rules.
"""
    with open("security_memo.txt", "w") as f:
        f.write(security_memo.strip())

    # 2. EC2 Inventory EU
    ec2_eu = [
        # 目标3：GPU，无CostCenter，闲置，但带SecurityLevel=High且无ApprovedBy -> 伪装的豁免，需惩罚
        {
            "InstanceId": "i-eu000000000000001",
            "InstanceType": "p3.8xlarge",
            "LaunchTime": "2023-10-02T10:00:00Z",
            "Tags": [{"Key": "SecurityLevel", "Value": "High"}]
        },
        # 陷阱4：GPU，无CostCenter，闲置，但带SecurityLevel=High且有ApprovedBy -> 真豁免，忽略
        {
            "InstanceId": "i-eu000000000000002",
            "InstanceType": "g4dn.2xlarge",
            "LaunchTime": "2023-10-05T14:00:00Z",
            "Tags": [{"Key": "SecurityLevel", "Value": "High"}, {"Key": "ApprovedBy", "Value": "Sec-John"}]
        },
        # 目标4：常规符合原红线的GPU
        {
            "InstanceId": "i-eu000000000000003",
            "InstanceType": "p4d.24xlarge",
            "LaunchTime": "2023-10-20T00:00:00Z",
            "Tags": [{"Key": "Env", "Value": "Dev"}]
        }
    ]
    with open("raw_data/eu_central/ec2_inventory.json", "w") as f:
        json.dump({"Reservations": [{"Instances": ec2_eu}]}, f, indent=2)

    # 3. CloudTrail Logs EU (故意让所有的目标机型都没有StartInstances记录)
    log_data_eu = {
        "Records": [
            {
                "eventTime": "2023-10-27T11:00:00Z",
                "eventName": "RunInstances",
                "responseElements": {
                    "instancesSet": {
                        "items": [
                            {"instanceId": "i-eu999999999999999"} # 无关实例
                        ]
                    }
                }
            }
        ]
    }
    with open("raw_data/eu_central/cloudtrail_logs/log_eu_001.json", "w") as f:
        json.dump(log_data_eu, f, indent=2)

def build_turn_3():
    os.makedirs("finance_data", exist_ok=True)
    
    # 构建价格表
    pricing_data = [
        ["InstanceType", "HourlyRateUSD"],
        ["p3.2xlarge", "3.06"],
        ["p3.8xlarge", "12.24"],
        ["p4d.24xlarge", "32.77"],
        ["g4dn.xlarge", "0.526"],
        ["g4dn.2xlarge", "0.752"],
        ["g5.12xlarge", "5.672"],
        ["m5.large", "0.096"]
    ]
    
    with open("finance_data/pricing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(pricing_data)

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
