import os
import json
import random
import string
import yaml
from datetime import datetime, timedelta

def generate_id():
    return "i-0" + "".join(random.choices(string.hexdigits.lower(), k=16))

def build_env():
    # 建立多级目录树
    base_dirs = ["hw_specs", "infra_dump", "audit_trails", "ops_action", "backup_garbage"]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)
        
    # ==========================================
    # 1. 生成碎片化的硬件规格库 (hw_specs)
    # ==========================================
    gpu_types = ["p4d.24xlarge", "g5.12xlarge", "g4dn.xlarge", "p3.8xlarge", "g3.4xlarge"]
    cpu_types = ["t3.micro", "m5.large", "c5.xlarge", "r5.2xlarge", "t4g.nano"]
    
    # 将规格打散到不同的文件和格式中
    hw_specs_1 = {"instances": [{"type": t, "accelerator_type": "GPU", "vcpus": 96} for t in gpu_types[:2]] + 
                               [{"type": t, "accelerator_type": "None", "vcpus": 2} for t in cpu_types[:2]]}
    hw_specs_2 = [{"instance_model": t, "specs": {"accelerator_type": "GPU", "memory": "256G"}} for t in gpu_types[2:]]
    hw_specs_3 = {"known_types": [{"id": t, "accelerator_type": "None"} for t in cpu_types[2:]]}
    
    with open("hw_specs/vendor_a.json", "w") as f: json.dump(hw_specs_1, f)
    with open("hw_specs/legacy_specs.yaml", "w") as f: yaml.dump(hw_specs_2, f)
    with open("hw_specs/sub_dir/vendor_b.json", "w") as f: 
        os.makedirs("hw_specs/sub_dir", exist_ok=True)
        json.dump(hw_specs_3, f)

    # ==========================================
    # 2. 生成恶心的资产盘点表 (infra_dump)
    # ==========================================
    regions = ["us-east-1", "us-west-2", "eu-central-1", "ap-northeast-1"]
    delimiters = ["|", ",", ";", "~", ":::"]
    
    all_instances = []
    zombie_candidates = [] # 记录真实的僵尸机候选(GPU, running, no CostCenter)
    active_gpus = []       # 记录有活动的GPU(GPU, running, no CostCenter, 稍后注入活跃日志)
    
    # 构造500台机器
    for _ in range(500):
        is_gpu = random.random() < 0.3
        i_type = random.choice(gpu_types) if is_gpu else random.choice(cpu_types)
        i_state = random.choice(["running", "running", "running", "stopped", "terminated"])
        
        has_costcenter = random.random() < 0.5
        tags = []
        if has_costcenter:
            tags.append(f"CostCenter={random.randint(1000, 9999)}")
        if random.random() < 0.8:
            tags.append(f"Owner=User{random.randint(1, 50)}")
        if random.random() < 0.5:
            tags.append(f"Env={random.choice(['Prod', 'Dev', 'Test'])}")
            
        tags_str = "&".join(tags) if tags else "None"
        i_id = generate_id()
        
        instance_obj = {
            "id": i_id, "type": i_type, "state": i_state, "tags": tags_str, "is_gpu": is_gpu
        }
        all_instances.append(instance_obj)
        
        # 分流：真正的僵尸 vs 假僵尸（有活跃日志）
        if is_gpu and i_state == "running" and not has_costcenter:
            if random.random() < 0.4:
                zombie_candidates.append(i_id)
            else:
                active_gpus.append(i_id)

    # 将资产分配到不同区域文件，且每个文件分隔符不同
    random.shuffle(all_instances)
    chunk_size = len(all_instances) // len(regions)
    
    for i, region in enumerate(regions):
        os.makedirs(f"infra_dump/{region}", exist_ok=True)
        delim = random.choice(delimiters)
        chunk = all_instances[i*chunk_size : (i+1)*chunk_size]
        
        with open(f"infra_dump/{region}/inventory.log", "w", encoding="utf-8") as f:
            f.write(f"# DUMP TIME: {datetime.utcnow().isoformat()}\n")
            f.write(f"# DELIMITER={delim}\n")
            f.write(f"# COLUMNS: INSTANCE_ID{delim}INSTANCE_TYPE{delim}STATUS{delim}TAGS\n")
            for inst in chunk:
                f.write(f"{inst['id']}{delim}{inst['type']}{delim}{inst['state']}{delim}{inst['tags']}\n")

    # ==========================================
    # 3. 构造海量混淆的审计日志 (audit_trails)
    # ==========================================
    # 生成基础干扰日志（readOnly: True）
    logs = []
    for _ in range(2000):
        logs.append({
            "eventTime": (datetime.utcnow() - timedelta(minutes=random.randint(1, 40000))).isoformat() + "Z",
            "eventName": random.choice(["DescribeInstances", "DescribeVolumes", "ListTagsForResource"]),
            "readOnly": True,
            "requestParameters": {
                "instanceId": random.choice(all_instances)['id'] if random.random() < 0.5 else "i-unknown"
            }
        })
        
    # 为 active_gpus 注入实质性业务事件（readOnly: False）
    for a_id in active_gpus:
        # 每个活跃机可能有多条活跃日志
        for _ in range(random.randint(1, 3)):
            logs.append({
                "eventTime": (datetime.utcnow() - timedelta(minutes=random.randint(1, 10000))).isoformat() + "Z",
                "eventName": random.choice(["StartInstances", "RunTask", "UpdateModel", "AttachVolume"]),
                "readOnly": False, # 关键标识！
                "requestParameters": {
                    "resources": {
                        "targetId": a_id # ID 潜伏在嵌套结构中
                    },
                    "actionContext": "business-critical"
                }
            })

    # 为一些 CPU 机和 Stopped 机注入活跃日志（干扰项）
    for _ in range(300):
        logs.append({
            "eventName": "SomeBusinessAction",
            "readOnly": False,
            "requestParameters": {
                "instanceId": random.choice(all_instances)['id']
            }
        })

    # 将日志打散到30个文件夹里的多个碎片文件中
    random.shuffle(logs)
    for i, log_event in enumerate(logs):
        day = (i % 30) + 1
        dir_path = f"audit_trails/2023/10/{day:02d}"
        os.makedirs(dir_path, exist_ok=True)
        file_idx = (i // 30) % 5
        
        filepath = f"{dir_path}/trail_shard_{file_idx}.json"
        
        # 逐条追加模拟碎片化日志
        mode = "a" if os.path.exists(filepath) else "w"
        with open(filepath, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write('{"Records": [\n')
                f.write(json.dumps(log_event))
            else:
                f.write(',\n' + json.dumps(log_event))
                
    # 封闭 JSON 数组
    for root, dirs, files in os.walk("audit_trails"):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), "a", encoding="utf-8") as f:
                    f.write('\n]}')

    # ==========================================
    # 4. 生成一些极具诱惑性的垃圾文件
    # ==========================================
    with open("backup_garbage/kill_list.json", "w") as f:
        # 伪造的一个错误的答案文件，测试 Agent 是否会盲目读取现成文件
        json.dump(["i-1111111111111111", "i-2222222222222222"], f)
        
    with open("ops_action/README.md", "w") as f:
        f.write("Target output file is `kill_list.json` in this directory. Must be a flat JSON array of strings.")
