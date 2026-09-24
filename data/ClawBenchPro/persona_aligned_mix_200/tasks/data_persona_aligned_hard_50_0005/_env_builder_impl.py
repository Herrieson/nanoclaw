import os
import json
import random
import binascii

def generate_hex_garbage(length=12):
    return binascii.b2a_hex(os.urandom(length)).decode('utf-8')

def create_broken_file(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def build_env():
    # 建立目录结构
    os.makedirs("billing_dumps", exist_ok=True)
    os.makedirs("metrics_archives/shards", exist_ok=True)
    os.makedirs("policies/org_tree", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 生成极度碎片化的 policies
    teams = [
        ("ai-core", "alice.ai@mega-corp.local", "old.alice@mega-corp.local"),
        ("ai-research", "bob.research@mega-corp.local", "old.bob@mega-corp.local"),
        ("data-eng", "charlie.data@mega-corp.local", "old.charlie@mega-corp.local"),
        ("bi-analytics", "david.bi@mega-corp.local", "old.david@mega-corp.local")
    ]
    
    for team, email, old_email in teams:
        depth_path = f"policies/org_tree/region_{random.randint(1,5)}/bu_{generate_hex_garbage(2)}/cc_{random.randint(100,999)}"
        os.makedirs(depth_path, exist_ok=True)
        
        # 存活 Active 版本
        active_data = {
            "node_meta": {"created": "2023", "hash": generate_hex_garbage(4)},
            "config": {
                "status": "active",
                "team_tag": team,
                "finops_contact": {"role": "Lead", "email": email}
            }
        }
        with open(os.path.join(depth_path, f"{team}_v2.json"), "w") as f:
            json.dump(active_data, f)
            
        # 废弃 Archived 版本（诱饵）
        archived_data = {
            "node_meta": {"created": "2021", "hash": generate_hex_garbage(4)},
            "config": {
                "status": "archived",
                "team_tag": team,
                "finops_contact": {"role": "Lead", "email": old_email}
            }
        }
        with open(os.path.join(depth_path, f"{team}_v1.json"), "w") as f:
            json.dump(archived_data, f)
            
    # 随便弄点垃圾策略文件
    for _ in range(10):
        d_path = f"policies/org_tree/garbage_{generate_hex_garbage(2)}"
        os.makedirs(d_path, exist_ok=True)
        with open(os.path.join(d_path, f"cfg_{generate_hex_garbage(2)}.json"), "w") as f:
            json.dump({"config": {"status": "archived", "team_tag": "unknown", "finops_contact": {"email": "null"}}}, f)

    # 2. Inventory - IP 到 ID 映射表
    inventory_lines = ["VPC,Subnet,Internal_IP,Instance_ID,Status"]
    inventory_lines.append(f"vpc-xyz,subnet-xyz,10.0.1.15,i-0ffff111111111111,running") # 目标低利用率
    inventory_lines.append(f"vpc-xyz,subnet-xyz,10.0.1.22,i-0ffff222222222222,running") # 干扰项
    inventory_lines.append(f"vpc-xyz,subnet-xyz,10.0.1.33,i-0ffff333333333333,running") # 干扰项
    create_broken_file("inventory/subnet_map.csv", inventory_lines)

    # 3. GPU 碎片化遥测日志
    logs = []
    base_time = 1698710400 
    for i in range(20): # 20个采集点
        ts = base_time + (i * 3600)
        # 目标: 全程低于 0.05
        logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ eth0_ip:10.0.1.15 ^^ gpu_util:0.0{random.randint(1,4)} ^^ mem:12%")
        # 干扰: 始终很高
        logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ eth0_ip:10.0.1.22 ^^ gpu_util:0.{random.randint(60,95)} ^^ mem:80%")
        # 干扰: 偶尔低，但超过0.05
        util = random.choice([0.01, 0.45, 0.50, 0.03])
        logs.append(f"{ts} ^^ 0x{generate_hex_garbage(4)} ^^ eth0_ip:10.0.1.33 ^^ gpu_util:{util:.2f} ^^ mem:40%")

    for _ in range(500): # 脏数据
        logs.append(f"TIMEOUT ^^ 0x{generate_hex_garbage(4)} ^^ eth0_ip:10.0.X.X ^^ NULL ^^ NULL")
        
    random.shuffle(logs)
    
    # 散布到 50 个 shard 文件
    for s_idx in range(50):
        shard_logs = logs[s_idx::50]
        ext = random.choice([".log", ".txt", ".tmp"])
        create_broken_file(f"metrics_archives/shards/shard_{s_idx:03d}{ext}", shard_logs)

    # 4. 恶心的 CUR 账单分段
    # 准备目标与干扰条目
    target_ebs_1 = f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd111111111111 | TYPE:EBS | STATUS:detached | TAGS:{{\"env\":\"prod\", \"team\":\"ai-core\"}} | COST:250.00"
    target_ebs_2 = f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd222222222222 | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"data-eng\"}} | COST:15.00"
    target_ebs_3 = f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd333333333333 | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"ghost-team\"}} | COST:12.00" # ghost-team match "unknown"
    
    fake_ebs_9m = f"0x{generate_hex_garbage()} || [REC] > ID:vol-0ffffffffffffffff | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"ai-core\"}} | COST:999.00" # 9月份的干扰
    
    ec2_rec_1 = f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff111111111111 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"ai-research\"}} | COST:2050.00"
    ec2_rec_2 = f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff222222222222 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"data-eng\"}} | COST:3000.00"
    ec2_rec_3 = f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff333333333333 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"bi-analytics\"}} | COST:1500.00"

    months_setup = [
        ("2023/09", [fake_ebs_9m]),
        ("2023/10", [target_ebs_1, target_ebs_2, target_ebs_3, ec2_rec_1, ec2_rec_2, ec2_rec_3])
    ]

    for month_dir, special_records in months_setup:
        for day in range(1, 32): # 生成31天的文件夹
            day_path = f"billing_dumps/{month_dir}/{day:02d}"
            os.makedirs(day_path, exist_ok=True)
            
            # 每天生成 5 个分片
            for part in range(5):
                daily_records = []
                # 塞入大量十六进制垃圾
                for _ in range(10):
                    daily_records.append(f"0x{generate_hex_garbage()} || [GARBAGE] {generate_hex_garbage(30)}")
                    daily_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:corrupted | TYPE:UNKNOWN | STATUS:null | TAGS:{{}} | COST:NaN")
                
                # 在 10月 的特定日子(比如15号) 插入特别记录
                if month_dir == "2023/10" and day == 15 and part == 0:
                    daily_records.extend(special_records)
                # 9月特定日子插入干扰记录
                if month_dir == "2023/09" and day == 10 and part == 0:
                    daily_records.extend(special_records)

                random.shuffle(daily_records)
                ext = random.choice([".dump", ".txt", ".tmp"])
                create_broken_file(f"{day_path}/part-{part:03d}{ext}", daily_records)

if __name__ == '__main__':
    build_env()
