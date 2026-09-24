import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 创建相关目录 (注意：当前工作目录已经是 assets/data_persona_aligned_base_50_0028/)
    dirs = ["infra_dump", "audit_trails", "iam_configs", "ops_action"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # 1. 生成非标准格式的 EC2 资产清单
    inventory_data = [
        # [时间戳] ||| 实例ID ||| 实例类型 ||| 状态 ||| TAGS:标签对 ||| METADATA:十六进制
        # 僵尸机 1：GPU，running，无 CostCenter，日志中无活跃事件
        "2023-10-27T10:01:23Z ||| i-0abcd1234efgh5678 ||| p4d.24xlarge ||| running ||| TAGS:Env=Dev;Team=AI_Research ||| METADATA:0x7B2A9",
        # 僵尸机 2：GPU，running，无 CostCenter，日志中无活跃事件
        "2023-10-27T10:02:45Z ||| i-01112223334445556 ||| g5.12xlarge ||| running ||| TAGS:Project=LLM_Test ||| METADATA:0x9C4F1",
        # 正常机 1：非 GPU，忽略
        "2023-10-27T10:05:11Z ||| i-0987654321fedcba0 ||| t3.micro ||| running ||| TAGS:Env=Prod ||| METADATA:0x00000",
        # 正常机 2：GPU，running，有 CostCenter，不是目标
        "2023-10-27T10:07:33Z ||| i-0aaabbbcccdddeee1 ||| p4d.24xlarge ||| running ||| TAGS:CostCenter=8892;Team=Core ||| METADATA:0x11111",
        # 正常机 3：GPU，已停止，不是目标
        "2023-10-27T10:08:12Z ||| i-02222222222222222 ||| g4dn.2xlarge ||| stopped ||| TAGS:Env=Dev ||| METADATA:0xFFFFF",
        # 活跃机：GPU，running，无 CostCenter，但日志中有活跃事件（不应被杀）
        "2023-10-27T10:11:55Z ||| i-0deadbeefdeadbeef ||| g4dn.xlarge ||| running ||| TAGS:Name=Experiment_X ||| METADATA:0x12345"
    ]
    
    with open("infra_dump/ec2_raw_inventory.log", "w", encoding="utf-8") as f:
        f.write("# INTERNAL ASSET DUMP v2.4.1\n")
        f.write("# FORMAT: TIMESTAMP ||| INSTANCE_ID ||| INSTANCE_TYPE ||| STATE ||| TAGS ||| METADATA\n")
        f.write("=========================================================================================\n")
        for line in inventory_data:
            f.write(line + "\n")
            
    # 2. 生成嵌套极深、充斥噪音的 CloudTrail 日志
    def generate_noise_record():
        return {
            "eventVersion": "1.08",
            "userIdentity": {
                "type": "AssumedRole",
                "principalId": f"AROA{random.randint(1000,9999)}:session-{random.randint(10,99)}",
                "arn": "arn:aws:sts::123456789012:assumed-role/NoiseRole/Session",
                "sessionContext": {
                    "attributes": {
                        "mfaAuthenticated": "false",
                        "creationDate": datetime.utcnow().isoformat() + "Z"
                    }
                }
            },
            "eventTime": datetime.utcnow().isoformat() + "Z",
            "eventSource": "ec2.amazonaws.com",
            "eventName": random.choice(["DescribeSecurityGroups", "DescribeVpcs", "DescribeVolumes"]),
            "awsRegion": "us-west-2",
            "sourceIPAddress": f"192.168.1.{random.randint(1,255)}",
            "userAgent": "aws-cli/2.0.0 Python/3.8.2 Linux/5.4.0",
            "requestParameters": None,
            "responseElements": None,
            "readOnly": True,
            "eventType": "AwsApiCall"
        }

    records = [generate_noise_record() for _ in range(50)]
    
    # 插入对僵尸机的只读事件 (DescribeInstanceStatus)
    records.append({
        "eventVersion": "1.08",
        "eventName": "DescribeInstanceStatus",
        "readOnly": True,
        "requestParameters": {
            "instancesSet": {
                "items": [{"instanceId": "i-0abcd1234efgh5678"}, {"instanceId": "i-01112223334445556"}]
            }
        },
        "responseElements": {"status": "success"}
    })
    
    # 插入对活跃机的实质性业务操作 (SubmitTrainingJob)
    records.append({
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "AssumedRole",
            "principalId": "AROAAI_TEAM_ROLE:job-runner"
        },
        "eventName": "SubmitTrainingJob",
        "readOnly": False,
        "requestParameters": {
            "jobName": "llm-fine-tuning-001",
            "clusterConfig": {
                "instanceCount": 1,
                "targetInstances": ["i-0deadbeefdeadbeef"],
                "hyperParameters": {"epochs": 10, "batch_size": 32}
            }
        },
        "responseElements": {"jobId": "job-9988776655"}
    })
    
    # 插入对活跃机的另一种业务操作 (UpdateModel)
    records.append({
         "eventVersion": "1.08",
         "eventName": "UpdateModel",
         "readOnly": False,
         "requestParameters": {
             "modelId": "v2.1-beta",
             "deploymentTarget": "i-0deadbeefdeadbeef"
         }
    })

    # 打乱日志顺序并分片保存，模拟真实复杂的审计日志结构
    random.shuffle(records)
    
    trail_1 = {"Records": records[:30]}
    trail_2 = {"Records": records[30:]}
    
    with open("audit_trails/trail_20231027_part1.json", "w") as f:
        json.dump(trail_1, f, indent=2)
    with open("audit_trails/trail_20231027_part2.json", "w") as f:
        json.dump(trail_2, f, indent=2)

    # 3. 生成复杂的 IAM 策略文件作为干扰信息（干扰项，考验 Agent 提取真正有用信息的能力）
    iam_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowAITeamGPUAccess",
                "Effect": "Allow",
                "Action": [
                    "ec2:RunInstances",
                    "ec2:StartInstances",
                    "ec2:StopInstances"
                ],
                "Resource": "arn:aws:ec2:*:*:instance/*",
                "Condition": {
                    "StringEquals": {
                        "ec2:InstanceType": ["p4d.24xlarge", "g5.12xlarge", "g4dn.xlarge"]
                    }
                }
            },
            {
                "Sid": "EnforceTaggingUsuallyButFailedHere",
                "Effect": "Allow",
                "Action": "ec2:CreateTags",
                "Resource": "arn:aws:ec2:*:*:instance/*"
            }
        ]
    }
    with open("iam_configs/policy_ai_team.json", "w") as f:
        json.dump(iam_policy, f, indent=4)
        
    with open("iam_configs/policy_readonly.yaml", "w") as f:
        f.write("---\nVersion: '2012-10-17'\nStatement:\n  - Effect: Allow\n    Action:\n      - ec2:Describe*\n    Resource: '*'\n")
