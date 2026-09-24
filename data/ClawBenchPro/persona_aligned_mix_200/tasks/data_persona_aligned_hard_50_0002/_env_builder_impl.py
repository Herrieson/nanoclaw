import os
import random
import datetime
import string
import json
import hashlib

def generate_ansi_noise():
    colors = ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m', '\x1b[35m', '\x1b[36m', '\x1b[90m', '\x1b[0m']
    return random.choice(colors)

def generate_hex_dump():
    lines = []
    for _ in range(random.randint(5, 12)):
        addr = f"{random.randint(0, 0xFFFFFFFF):08x}"
        hex_data = " ".join([f"{random.randint(0, 255):02x}" for _ in range(16)])
        chars = "".join([random.choice(string.ascii_letters + string.digits + ".") for _ in range(16)])
        lines.append(f"    {addr}  {hex_data}  |{chars}|")
    return "\n".join(lines)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_log_content(region, is_target=False, is_decoy=False, decoy_type=None):
    lines = []
    
    # 确定时间基准
    if is_target:
        # Target: 04:xx UTC
        start_time = datetime.datetime(2023, 10, 27, 4, random.randint(10, 50), random.randint(0, 59))
    elif is_decoy and decoy_type == "time_decoy":
        # Decoy 1: Same region (EU), but different time (e.g., 01:xx UTC or 14:xx UTC)
        start_time = datetime.datetime(2023, 10, 27, random.choice([1, 2, 8, 14, 20]), random.randint(0, 59), random.randint(0, 59))
    elif is_decoy and decoy_type == "region_decoy":
        # Decoy 2: Target time (04:xx), but wrong region (e.g., US)
        start_time = datetime.datetime(2023, 10, 27, 4, random.randint(10, 50), random.randint(0, 59))
    else:
        # Random noise
        start_time = datetime.datetime(2023, 10, 27, random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))

    # 1. 大量噪音日志
    for i in range(random.randint(200, 500)):
        ts = (start_time + datetime.timedelta(seconds=i*0.5)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        thread_id = f"T-{random.randint(100, 999)}"
        ansi = generate_ansi_noise()
        
        noise_type = random.random()
        if noise_type < 0.4:
            hash_val = "".join(random.choices(string.hexdigits.lower(), k=64))
            lines.append(f"{ansi}[{ts}] [{thread_id}] Step 4/15 : Pulling fs layer {hash_val[:12]}\x1b[0m")
        elif noise_type < 0.8:
            lines.append(f"{ansi}[{ts}] [{thread_id}] [WARNING] /usr/include/c++/11/bits/stl_map.h:{random.randint(100, 2000)}: warning: '{random_string()}_var' may be used uninitialized\x1b[0m")
        else:
            lines.append(f"[{ts}] [{thread_id}] [DEBUG] Evaluating CMake target {random_string()}...")

    # 2. 插入冲突逻辑 (Target 或 Decoy)
    if is_target or is_decoy:
        ts = (start_time + datetime.timedelta(seconds=250)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        thread_id = f"T-{random.randint(10, 99):03d}"
        
        if is_target:
            dep_id = "dep_id: 8f4c2e"
            v1, v2 = "3.3.9", "3.4.2"
        else:
            # 假线索的依赖 ID 和版本
            dep_id = f"dep_id: {random_string(6)}"
            v1, v2 = f"{random.randint(1,9)}.{random.randint(0,5)}.0", f"{random.randint(1,9)}.{random.randint(6,9)}.1"

        lines.append(f"\x1b[31m[{ts}] [{thread_id}] [FATAL] Dependency resolution failed for target 'hybrid-engine-core'.\x1b[0m")
        lines.append(f"\x1b[31m[{ts}] [{thread_id}] [FATAL] Conflict detected in transitive graph:\x1b[0m")
        # 故意隔开一些乱七八糟的噪音
        lines.append(f"[{ts}] [T-999] [INFO] Garbage collector invoked.")
        lines.append(f"\x1b[31m[{ts}] [{thread_id}] [FATAL]   -> module_{random_string(3)} requires '{dep_id}' (v{v1})\x1b[0m")
        lines.append(f"\x1b[31m[{ts}] [{thread_id}] [FATAL]   -> module_{random_string(3)} requires '{dep_id}' (v{v2})\x1b[0m")
        lines.append(f"\x1b[31m[{ts}] [{thread_id}] [FATAL] Aborting build. Hex dump of state:\x1b[0m")
        lines.append(generate_hex_dump())

    # 3. 扫尾噪音
    for i in range(random.randint(100, 200)):
        ts = (start_time + datetime.timedelta(seconds=260 + i)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        lines.append(f"[{ts}] [ERROR] Make command failed with exit code 2.")
        
    return "\n".join(lines)


def build_env():
    # 1. 构建离散分布的碎裂日志目录
    regions = ['eu-west-1', 'eu-central-1', 'eu-north-1', 'us-east-1', 'us-west-2', 'ap-southeast-1']
    
    os.makedirs("build_logs", exist_ok=True)
    for r in regions:
        os.makedirs(f"build_logs/{r}", exist_ok=True)
        # 每个区生成 10~20 个节点的日志文件
        for j in range(random.randint(10, 20)):
            job_id = f"job_{random_string(8)}"
            log_path = f"build_logs/{r}/{job_id}.log"
            
            # 判断是否是目标或者干扰
            is_target = False
            is_decoy = False
            decoy_type = None
            
            # 设定唯一真相：在 eu-central-1 产生真实的 04:xx 冲突
            if r == 'eu-central-1' and j == 7:  # 硬编码一个特定的位置保证绝对触发
                is_target = True
            elif r.startswith('eu') and random.random() < 0.15:
                is_decoy = True
                decoy_type = "time_decoy" # 欧洲区，但时间不是四点
            elif not r.startswith('eu') and random.random() < 0.2:
                is_decoy = True
                decoy_type = "region_decoy" # 四点，但不是欧洲区
                
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(generate_log_content(r, is_target=is_target, is_decoy=is_decoy, decoy_type=decoy_type))

    # 2. 构建分片化的注册表数据库
    os.makedirs("registry_db", exist_ok=True)
    
    # 我们将生成 256 个分片文件
    target_dep_id = "8f4c2e"
    target_pkg_name = "lib_eigen_tensor_v2"
    
    # 确定目标 ID 存在哪个分片
    target_shard = int(hashlib.md5(target_dep_id.encode()).hexdigest()[:2], 16)
    
    for shard_idx in range(256):
        shard_file = f"registry_db/shard_{shard_idx:02x}.json"
        
        packages = []
        # 每个分片塞入 150 个无用的包映射
        for _ in range(150):
            packages.append({
                "id": random_string(6),
                "pkg_name": f"pkg_{random_string(4)}_{random_string(6)}",
                "maintainer": f"team_{random_string(2)}",
                "internal_repo": f"git.corp.local/deps/pkg_{random_string(4)}.git"
            })
            
        # 如果是命中的分片，把真实目标混进去
        if shard_idx == target_shard:
            packages.append({
                "id": target_dep_id,
                "pkg_name": target_pkg_name,
                "maintainer": "core_infra_team",
                "internal_repo": "git.corp.local/core/lib_eigen_tensor_v2.git"
            })
            random.shuffle(packages)
            
        with open(shard_file, "w", encoding="utf-8") as f:
            json.dump({"schema": "v3.1", "shard_id": f"{shard_idx:02x}", "packages": packages}, f, indent=2)

if __name__ == "__main__":
    build_env()
