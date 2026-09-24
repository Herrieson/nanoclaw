import os
import json
import random
import binascii

def generate_hex_garbage(length=8):
    return binascii.b2a_hex(os.urandom(length)).decode('utf-8')

def build_env():
    # 创建所有必须的目录（纯相对路径，绝对服从沙盒环境要求）
    os.makedirs("billing_dumps", exist_ok=True)
    os.makedirs("metrics_archives", exist_ok=True)
    os.makedirs("policies", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 构造极其反人类嵌套层级的 Tag 策略矩阵
    tag_matrix = {
        "enterprise_hierarchy": {
            "global_regions": {
                "ap-northeast-1": {
                    "business_units": [
                        {
                            "bu_name": "AI_Division",
                            "cost_centers": {
                                "cc_1001": {
                                    "team_tag": "ai-core",
                                    "finops_contact": {"role": "Lead", "email": "alice.ai@mega-corp.local"}
                                },
                                "cc_1002": {
                                    "team_tag": "ai-research",
                                    "finops_contact": {"role": "Scientist", "email": "bob.research@mega-corp.local"}
                                }
                            }
                        },
                        {
                            "bu_name": "Data_Platform",
                            "cost_centers": {
                                "cc_2001": {
                                    "team_tag": "data-eng",
                                    "finops_contact": {"role": "Engineer", "email": "charlie.data@mega-corp.local"}
                                },
                                "cc_2002": {
                                    "team_tag": "bi-analytics",
                                    "finops_contact": {"role": "Analyst", "email": "david.bi@mega-corp.local"}
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    with open("policies/tag_matrix.json", "w", encoding="utf-8") as f:
        json.dump(tag_matrix, f, indent=2)

    # 2. 构造极其混乱的 CUR 账单导出文本，混合十六进制、不规范的分隔符
    cur_records = []
    
    # [目标记录] 闲置的 EBS (detached)
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd111111111111 | TYPE:EBS | STATUS:detached | TAGS:{{\"env\":\"prod\", \"team\":\"ai-core\"}} | COST:250.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd222222222222 | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"data-eng\"}} | COST:15.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd333333333333 | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"unknown-team\"}} | COST:12.00")
    
    # [干扰记录] 正常挂载的 EBS (in-use / attached)
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd999999999999 | TYPE:EBS | STATUS:in-use | TAGS:{{\"team\":\"ai-research\"}} | COST:100.00")
    
    # [记录] EC2 实例元数据（用于后续通过遥测日志寻找 GPU 低利用率资源）
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff111111111111 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"ai-research\"}} | COST:2050.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff222222222222 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"data-eng\"}} | COST:3000.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff333333333333 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"bi-analytics\"}} | COST:1500.00")

    # 混入大量脏数据与截断的数据
    for _ in range(30):
        cur_records.append(f"0x{generate_hex_garbage()} || [GARBAGE_DUMP] NULL FATAL_ERR << 0x{generate_hex_garbage(16)}")
        cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:corrupted-id | TYPE:UNKNOWN | STATUS:null | TAGS:{{brok[en... | COST:NaN")

    random.shuffle(cur_records)
    with open("billing_dumps/cur_raw_202310.txt", "w", encoding="utf-8") as f:
        for rec in cur_records:
            f.write(rec + "\n")

    # 3. 构造非标准格式的 GPU 遥测监控日志 (带有奇葩的 ^^ 分隔符)
    gpu_logs = []
    base_time = 1698710400 
    
    for i in range(12): # 生成多个时间点的数据
        ts = base_time + (i * 3600)
        
        # [目标记录] i-0ffff111111111111 (ai-research): 长期超低利用率 (< 5%)
        gpu_logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ i-0ffff111111111111 ^^ gpu_util:0.0{random.randint(1,4)} ^^ mem:12%")
        
        # [干扰记录] i-0ffff222222222222 (data-eng): 正常高利用率
        gpu_logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ i-0ffff222222222222 ^^ gpu_util:0.{random.randint(60,95)} ^^ mem:80%")
        
        # [干扰记录] i-0ffff333333333333 (bi-analytics): 偶尔低，但平均高于 5%
        util = random.choice([0.01, 0.45, 0.50, 0.10])
        gpu_logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ i-0ffff333333333333 ^^ gpu_util:{util:.2f} ^^ mem:40%")

        # 随机干扰实例和其他脏数据
        gpu_logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ i-09999999999999999 ^^ gpu_util:0.50 ^^ mem:50%")
        gpu_logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ METRIC_TIMEOUT ^^ ERROR ^^ NULL")

    random.shuffle(gpu_logs)
    with open("metrics_archives/gpu_telemetry.log", "w", encoding="utf-8") as f:
        for log in gpu_logs:
            f.write(log + "\n")

if __name__ == '__main__':
    build_env()
