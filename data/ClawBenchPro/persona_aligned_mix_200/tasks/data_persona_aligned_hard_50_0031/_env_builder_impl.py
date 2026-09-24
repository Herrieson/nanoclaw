import os
import random
import yaml

def build_env():
    # 1. 创建碎片化的目录结构
    os.makedirs("src", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    for i in range(5):
        os.makedirs(f"logs/node_{i}", exist_ok=True)
        
    for i in range(10):
        os.makedirs(f"packet_vault/shard_{i}", exist_ok=True)

    # 2. 写入 C 头文件 (线索 1：查找 ERR_MALFORMED 的整数值)
    header_content = """#ifndef XDP_ERRORS_H
#define XDP_ERRORS_H

#define ERR_OK 0
#define ERR_RATE_LIMIT 1
#define ERR_GEOIP 2
#define ERR_BLACKLIST 3
#define ERR_MALFORMED 4
#define ERR_SPOOF 8
#define ERR_PROTOCOL 15

#endif
"""
    with open("src/xdp_errors.h", "w") as f:
        f.write(header_content)

    # 3. 生成安全策略与白名单 (线索 2 & 3：必须排除白名单 IP)
    policy_content = {
        "security": {
            "mode": "strict",
            "active_whitelist_file": "safe_ips_v2.txt",
            "max_bans_per_min": 1000
        }
    }
    with open("config/policies.yaml", "w") as f:
        yaml.dump(policy_content, f)

    # 干扰白名单
    with open("config/safe_ips_v1.txt", "w") as f:
        f.write("# 废弃的白名单\n8.8.8.8\n120.44.55.66\n")

    # 真实白名单 (包含了一个同时也会触发 ERR_MALFORMED 的内网探针 IP，作为过滤陷阱)
    with open("config/safe_ips_v2.txt", "w") as f:
        f.write("# 核心探针与内网 DNS\n10.0.5.200\n192.168.1.1\n# 运维跳板机\n172.16.254.1\n")

    # 4. 预设 IP 与数据池
    # 目标：120.44.55.66, 45.33.22.11, 198.51.100.77 (10.0.5.200 将被剔除)
    malformed_ips = ["120.44.55.66", "45.33.22.11", "10.0.5.200", "198.51.100.77"]
    decoy_ips = ["203.0.113.1", "198.51.100.2", "1.1.1.1"] # 其他错误的 IP
    normal_ips = ["8.8.8.8", "192.168.100.1"]

    # 5. 生成大规模打散的数据
    # pkt_id 必须全局唯一
    pkt_id_counter = 100000 
    
    # 存放待写入各文件的数据
    log_files = {f"logs/node_{i}/trace_{j}.log": [] for i in range(5) for j in range(3)}
    dump_files = {f"packet_vault/shard_{i}/dump_{j}.txt": [] for i in range(10) for j in range(2)}
    
    noise_log_templates = [
        "ksoftirqd/0-9  [00{cpu}] d.s. {ts}: sched_switch: prev_comm=swapper/0 prev_pid=0 ==> next_comm=rcu_sched",
        "systemd-1       [00{cpu}] d... {ts}: sys_enter_openat: filename=... flags=0",
        "sshd-1284      [00{cpu}] d... {ts}: [TRUNCATED] \xDE\xAD\xBE\xEF buffer full at {ts}",
    ]

    base_time = 1715000000.000000
    
    packets = []
    # 构造核心业务数据
    for _ in range(80):
        packets.append({"ip": random.choice(malformed_ips), "reason": 4, "dev": "eth0"}) # 目标
    for _ in range(30):
        packets.append({"ip": random.choice(malformed_ips), "reason": 4, "dev": "eth1"}) # 接口陷阱
    for _ in range(100):
        packets.append({"ip": random.choice(decoy_ips), "reason": random.choice([1, 2, 8]), "dev": "eth0"}) # 错误码陷阱
    for _ in range(200):
        packets.append({"ip": random.choice(normal_ips), "reason": 0, "dev": "eth0"}) # 正常通行
        
    random.shuffle(packets)

    for pkt in packets:
        base_time += random.uniform(0.0001, 0.05)
        cpu = random.randint(0, 7)
        dec_id = pkt_id_counter
        pkt_id_counter += random.randint(1, 15) # 递增保证唯一性
        
        t_str = f"{base_time:.6f}"
        
        # --- 写入 Log ---
        log_lines = []
        # 随机噪音
        for _ in range(random.randint(0, 2)):
            log_lines.append(random.choice(noise_log_templates).format(cpu=cpu, ts=t_str))
            
        if pkt["reason"] == 0:
            log_lines.append(f"ksoftirqd/{cpu}-{cpu+9}  [00{cpu}] d.s1 {t_str}: bpf_trace_printk: [XDP_PASS] dev={pkt['dev']} pkt_id={dec_id} bytes={random.randint(64,1500)}")
        else:
            log_lines.append(f"ksoftirqd/{cpu}-{cpu+9}  [00{cpu}] d.s1 {t_str}: bpf_trace_printk: [XDP_DROP] dev={pkt['dev']} pkt_id={dec_id} reason={pkt['reason']}")
            
        target_log_file = random.choice(list(log_files.keys()))
        log_files[target_log_file].extend(log_lines)
        
        # --- 写入 Vault Dump ---
        # Vault 使用十六进制 ID，大写，8位补齐
        hex_id = f"0x{dec_id:08X}"
        dst_ip = f"10.200.0.{random.randint(1, 254)}"
        random_payload = "".join([f"{random.randint(0, 255):02X}" for _ in range(16)])
        
        dump_block = f"""[*] FRAME_START
    ID: {hex_id}
    > L3_INFO: SRC_IP={pkt['ip']}, DST_IP={dst_ip}
    > PAYLOAD: {random_payload}
[*] FRAME_END
"""     
        # 有极小概率混入损坏的乱码 Dump 来测试健壮性
        if random.random() < 0.05:
            dump_block += f"[!] BROKEN_FRAME_START\n    ID: 0x00000000\n    > L3_INFO: SRC_IP=UNKNOWN\n[*] FRAME_END\n"

        target_dump_file = random.choice(list(dump_files.keys()))
        dump_files[target_dump_file].append(dump_block)

    # 6. 将内存数据刷入磁盘文件
    for filepath, lines in log_files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            
    for filepath, blocks in dump_files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))

if __name__ == "__main__":
    build_env()
