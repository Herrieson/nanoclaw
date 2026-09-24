import os
import base64
import random
import json

def build_env():
    # 建立废土目录树
    dirs = [
        "sys_data/quarantine_zone",
        "sys_data/active_billing_v3",
        "metrics/telemetry_shards",
        "cmdb",
        "action_items"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    random.seed(42) # 保证环境可复现

    # ==========================================
    # 1. 制造线索：崩溃诊断日志 (指引真正的账单目录)
    # ==========================================
    crash_log = """[2023-10-24 03:15:22] CRITICAL ERROR: Pipeline memory leak detected.
[2023-10-24 03:15:25] ACTION: Corrupted stream flushed to `sys_data/quarantine_zone`. WARNING: Contains hallucinated resource IDs. DO NOT PROCESS.
[2023-10-24 03:18:00] RECOVERY: Pipeline restored. Validated billing stream redirected to `sys_data/active_billing_v3`.
[2023-10-24 03:18:05] SYSTEM: Awaiting manual review.
"""
    with open("crash_diagnostics.log", "w", encoding="utf-8") as f:
        f.write(crash_log)

    # ==========================================
    # 2. 制造计费碎片 (Fragmentation & Noise)
    # ==========================================
    # 目标答案
    real_idle_ebs = ["vol-0a1b2c3d4e5f60001", "vol-0a1b2c3d4e5f60002", "vol-0a1b2c3d4e5f60003"]
    real_inuse_ebs = ["vol-01111111111111111", "vol-02222222222222222"]
    fake_idle_ebs = ["vol-deadbeefdeadbeef1", "vol-deadbeefdeadbeef2"] # 放在隔离区

    def generate_billing_shard(path, num_files, ebs_list, is_idle):
        for i in range(num_files):
            file_name = f"shard_{i:03d}.dat"
            content = f"STREAM_HEADER|0x{random.randint(1000,9999)}\n"
            
            # 随机插入若干噪音行
            for _ in range(random.randint(5, 15)):
                content += f"WARN: DUMP 0x{random.randint(100000,999999)} -- IGNORED\n"
            
            # 插入实际数据
            if i < len(ebs_list):
                state = "available" if is_idle else "in-use"
                payload = json.dumps({
                    "resource_id": ebs_list[i],
                    "resource_type": "AWS::EC2::Volume",
                    "usage_type": "EBS:VolumeUsage.gp3",
                    "state": state,
                    "cost": round(random.uniform(10.0, 500.0), 2)
                }).encode('utf-8')
                b64_payload = base64.b64encode(payload).decode()
                content += f"0xBEAF DATA_STREAM: {b64_payload} END_STREAM\n"
            else:
                # 纯粹的废数据负载
                junk = json.dumps({"resource_type": "AWS::S3::Bucket", "status": "active"}).encode()
                content += f"0xBEAF DATA_STREAM: {base64.b64encode(junk).decode()} END_STREAM\n"

            with open(os.path.join(path, file_name), "w", encoding="utf-8") as f:
                f.write(content)

    # 生成隔离区（假数据，绝对不能提取这里的）
    generate_billing_shard("sys_data/quarantine_zone", 50, fake_idle_ebs, is_idle=True)
    # 生成健康区（真数据，包含空闲和非空闲，且文件分散）
    all_real_ebs = real_idle_ebs + real_inuse_ebs
    # 打乱后随机放置，is_idle由ID本身判定（我们在上面硬编码生成时自己知道）
    # 这里为了简便，直接按批次写入
    for i in range(100):
        content = f"LOG_OFFSET_{i}\n"
        if i == 12:
            p = base64.b64encode(json.dumps({"resource_id": real_idle_ebs[0], "resource_type": "AWS::EC2::Volume", "state": "available"}).encode()).decode()
            content += f"0xBEAF DATA_STREAM: {p} END_STREAM\n"
        elif i == 45:
            p = base64.b64encode(json.dumps({"resource_id": real_idle_ebs[1], "resource_type": "AWS::EC2::Volume", "state": "available"}).encode()).decode()
            content += f"0xBEAF DATA_STREAM: {p} END_STREAM\n"
        elif i == 88:
            p = base64.b64encode(json.dumps({"resource_id": real_idle_ebs[2], "resource_type": "AWS::EC2::Volume", "state": "available"}).encode()).decode()
            content += f"0xBEAF DATA_STREAM: {p} END_STREAM\n"
        elif i == 33:
            p = base64.b64encode(json.dumps({"resource_id": real_inuse_ebs[0], "resource_type": "AWS::EC2::Volume", "state": "in-use"}).encode()).decode()
            content += f"0xBEAF DATA_STREAM: {p} END_STREAM\n"
        elif i == 77:
            p = base64.b64encode(json.dumps({"resource_id": real_inuse_ebs[1], "resource_type": "AWS::EC2::Volume", "state": "in-use"}).encode()).decode()
            content += f"0xBEAF DATA_STREAM: {p} END_STREAM\n"
        else:
            p = base64.b64encode(json.dumps({"resource_type": "OTHER"}).encode()).decode()
            content += f"0xBEAF DATA_STREAM: {p} END_STREAM\n"
        
        with open(f"sys_data/active_billing_v3/fragment_{i:03d}.log", "w") as f:
            f.write(content)

    # ==========================================
    # 3. 制造多跳逻辑：CMDB映射表 & 指标碎片
    # ==========================================
    # 目标：找出真正的僵尸GPU
    zombie_gpus = [
        ("NODE-GPU-01", "i-0987654321gpu0001", "p4d.24xlarge", 0.5), # 目标
        ("NODE-GPU-02", "i-0987654321gpu0002", "g4dn.12xlarge", 1.8) # 目标
    ]
    busy_gpus = [
        ("NODE-GPU-03", "i-0987654321gpu0003", "g5.xlarge", 45.0), # 利用率高，忽略
        ("NODE-GPU-04", "i-0987654321gpu0004", "p3.8xlarge", 90.5) # 利用率高，忽略
    ]
    zombie_cpus = [
        ("NODE-CPU-01", "i-0987654321cpu0001", "m5.large", 0.1), # 利用率低，但是非GPU，忽略
        ("NODE-CPU-02", "i-0987654321cpu0002", "t3.medium", 1.5) # 利用率低，但是非GPU，忽略
    ]

    all_assets = zombie_gpus + busy_gpus + zombie_cpus

    # 生成 CMDB 文件 (带有大量噪音资产)
    with open("cmdb/enterprise_asset_registry.csv", "w", encoding="utf-8") as f:
        f.write("ASSET_TAG,AWS_INSTANCE_ID,INSTANCE_FAMILY,OWNER_DEPT\n")
        for asset in all_assets:
            f.write(f"{asset[0]},{asset[1]},{asset[2]},Core-Team\n")
        
        # 写入 500 行无用资产
        for i in range(500):
            f.write(f"NODE-UNK-{i},i-unknown{i:04d},r5.large,Unknown\n")

    # 生成 100 个指标碎片
    for i in range(100):
        with open(f"metrics/telemetry_shards/shard_{i:03d}.tsv", "w", encoding="utf-8") as f:
            f.write("@@ METRIC_DUMP\n")
            # 鬼畜分隔符 ' ~|~ '
            for _ in range(10):
                fake_node = f"NODE-UNK-{random.randint(0,499)}"
                f.write(f"[METRIC] ~|~ {fake_node} ~|~ N/A ~|~ {random.uniform(0.1, 99.0):.1f} ~|~ RUNNING\n")
            
            # 将真实资产随机混入碎片中
            for asset in all_assets:
                if random.random() < 0.05: # 每个资产有5%概率在当前碎片出现 (会保证它们至少出现一次的逻辑在下面补丁)
                    pass 

    # 确保目标资产一定被记录在特定的碎片中
    asset_placements = {
        15: [zombie_gpus[0], busy_gpus[0]],
        42: [zombie_cpus[0]],
        73: [zombie_gpus[1], zombie_cpus[1]],
        91: [busy_gpus[1]]
    }
    for shard_idx, assets in asset_placements.items():
        with open(f"metrics/telemetry_shards/shard_{shard_idx:03d}.tsv", "a", encoding="utf-8") as f:
            for a in assets:
                # 格式: [METRIC] ~|~ ASSET_TAG ~|~ GPU_UTIL_7D_AVG ~|~ CPU_UTIL_7D_AVG ~|~ STATUS
                gpu_util = f"{a[3]:.1f}" if "GPU" in a[0] else "N/A"
                f.write(f"[METRIC] ~|~ {a[0]} ~|~ {gpu_util} ~|~ {random.uniform(0.1, 10.0):.1f} ~|~ RUNNING\n")

if __name__ == "__main__":
    build_env()
