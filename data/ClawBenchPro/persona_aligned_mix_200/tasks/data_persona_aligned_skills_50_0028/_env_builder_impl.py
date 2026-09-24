import os
import json
import base64

def build_env():
    # 创建相关目录
    dirs = ["infra_dump", "audit_trails", "iam_configs", "ops_action"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # 1. 生成加密的 (Base64混淆) 非标准格式 EC2 资产清单
    # 真实逻辑数据：
    # 僵尸机 1：GPU(p4d)，running，无 CostCenter，日志中无活跃事件
    # 僵尸机 2：GPU(g5)，running，无 CostCenter，日志中无活跃事件
    # 正常机 1：非 GPU(t3)，忽略
    # 正常机 2：GPU(p4d)，running，有 CostCenter，不是目标
    # 正常机 3：GPU(g4dn)，已停止，不是目标
    # 活跃机：GPU(g4dn)，running，无 CostCenter，但日志中有活跃事件（不应被杀）
    
    raw_inventory_content = """# INTERNAL ASSET DUMP v3.0.1 (ENCRYPTED_BLOB)
# FORMAT: TIMESTAMP ||| INSTANCE_ID ||| INSTANCE_TYPE ||| STATE ||| TAGS ||| METADATA
=========================================================================================
2023-10-27T10:01:23Z ||| i-0abcd1234efgh5678 ||| p4d.24xlarge ||| running ||| TAGS:Env=Dev;Team=AI_Research ||| METADATA:0x7B2A9
2023-10-27T10:02:45Z ||| i-01112223334445556 ||| g5.12xlarge ||| running ||| TAGS:Project=LLM_Test ||| METADATA:0x9C4F1
2023-10-27T10:05:11Z ||| i-0987654321fedcba0 ||| t3.micro ||| running ||| TAGS:Env=Prod ||| METADATA:0x00000
2023-10-27T10:07:33Z ||| i-0aaabbbcccdddeee1 ||| p4d.24xlarge ||| running ||| TAGS:CostCenter=8892;Team=Core ||| METADATA:0x11111
2023-10-27T10:08:12Z ||| i-02222222222222222 ||| g4dn.2xlarge ||| stopped ||| TAGS:Env=Dev ||| METADATA:0xFFFFF
2023-10-27T10:11:55Z ||| i-0deadbeefdeadbeef ||| g4dn.xlarge ||| running ||| TAGS:Name=Experiment_X ||| METADATA:0x12345
"""
    
    # 混淆处理：将其编码为看起来像二进制 dump 的 base64 字符串
    encoded_data = base64.b64encode(raw_inventory_content.encode('utf-8')).decode('utf-8')
    # 插入一些伪造的二进制文件头尾特征
    fake_binary_wrapper = f"0xCAFEBABE_HEADER\n{encoded_data}\n0xDEADBEEF_EOF"
    
    with open("infra_dump/ec2_inventory.dat", "w", encoding="utf-8") as f:
        f.write(fake_binary_wrapper)
            
    # 2. 在 audit_trails 留个说明文件，告知日志已上云
    with open("audit_trails/README.txt", "w", encoding="utf-8") as f:
        f.write("WARNING: Local CloudTrail storage is deprecated due to compliance policy SEC-042.\n")
        f.write("All logs are now streamed to centralized SIEM (Splunk) and AWS Athena.\n")
        f.write("Please use the appropriate querying tools to inspect instance activities.\n")

    # 3. 生成复杂的 IAM 策略文件作为干扰信息
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
            }
        ]
    }
    with open("iam_configs/policy_ai_team.json", "w") as f:
        json.dump(iam_policy, f, indent=4)
