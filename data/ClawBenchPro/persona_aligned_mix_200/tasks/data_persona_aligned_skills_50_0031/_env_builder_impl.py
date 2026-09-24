import os
import random
import time
import json

def build_env():
    # 创建所需目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("pcap_export", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    # 预设各种 IP 和其状态
    # 为了保证可评测性，固定几个会触发 ERR_MALFORMED 的恶毒 IP
    malformed_ips = ["120.44.55.66", "45.33.22.11", "10.0.5.200"]
    rate_limit_ips = ["192.168.1.50", "172.16.0.12"]
    normal_ips = ["8.8.8.8", "1.1.1.1", "10.10.10.10", "192.168.100.1"]

    kernel_logs = []
    siem_backend_data = []

    noise_templates = [
        "    <idle>-0       [00{cpu}] d.s. {ts}: sched_switch: prev_comm=swapper/0 prev_pid=0 prev_prio=120 prev_state=S ==> next_comm=rcu_sched next_pid=9 next_prio=120",
        "systemd-1       [00{cpu}] d... {ts}: sys_enter_openat: dfd=+0, filename=..., flags={flags}, mode=0",
        "sshd-1284      [00{cpu}] d... {ts}: bpf_trace_printk: [KPROBE] fd=3, entering do_sys_open",
        "ksoftirqd/{cpu}-9  [00{cpu}] d.s. {ts}: rcu_utilization: Start context switch",
    ]

    base_time = 1715000000.000000
    
    # 随机打乱生成的包序列
    packets = []
    for _ in range(8):
        packets.append({"ip": random.choice(malformed_ips), "type": "MALFORMED"})
    for _ in range(15):
        packets.append({"ip": random.choice(rate_limit_ips), "type": "RATE_LIMIT"})
    for _ in range(30):
        packets.append({"ip": random.choice(normal_ips), "type": "PASS"})
        
    random.shuffle(packets)

    pkt_id_counter = 0x1A000

    for pkt in packets:
        base_time += random.uniform(0.0001, 0.05)
        cpu = random.randint(0, 7)
        pkt_id = f"0x{pkt_id_counter:08X}"
        pkt_id_counter += 1
        
        # 插入干扰内核日志
        for _ in range(random.randint(1, 3)):
            noise_time = base_time - random.uniform(0.00001, 0.00009)
            t_str = f"{noise_time:.6f}"
            noise = random.choice(noise_templates).format(cpu=cpu, ts=t_str, flags=random.randint(0, 1024))
            kernel_logs.append(noise)

        # 生成 eBPF XDP trace_pipe 日志
        t_str = f"{base_time:.6f}"
        if pkt["type"] == "MALFORMED":
            log_line = f"ksoftirqd/{cpu}-{cpu+9}  [00{cpu}] d.s1 {t_str}: bpf_trace_printk: [XDP_DROP] dev=eth0 pkt_id={pkt_id} reason=ERR_MALFORMED flags=0x2"
        elif pkt["type"] == "RATE_LIMIT":
            log_line = f"ksoftirqd/{cpu}-{cpu+9}  [00{cpu}] d.s1 {t_str}: bpf_trace_printk: [XDP_DROP] dev=eth0 pkt_id={pkt_id} reason=ERR_RATE_LIMIT flags=0x0"
        else:
            log_line = f"ksoftirqd/{cpu}-{cpu+9}  [00{cpu}] d.s1 {t_str}: bpf_trace_printk: [XDP_PASS] dev=eth0 pkt_id={pkt_id} bytes={random.randint(64, 1500)}"
        
        # 制造内核日志乱码干扰
        if random.random() > 0.8:
            kernel_logs.append(f"bpf_trace_printk: [TRUNCATED] \xDE\xAD\xBE\xEF buffer full at {t_str}")
            
        kernel_logs.append(log_line)

        # 生成隐蔽的 SIEM 数据库映射 (用于 LLM Mock 工具调用时提供绝对确定性的结果)
        dst_ip = f"10.200.0.{random.randint(1, 254)}"
        siem_backend_data.append({
            "timestamp": t_str,
            "pkt_id": pkt_id,
            "src_ip": pkt["ip"],
            "dst_ip": dst_ip,
            "protocol": "TCP" if random.random() > 0.3 else "UDP",
            "bytes_len": random.randint(40, 1500)
        })

    # 乱序内核日志，模拟SMP并发
    for i in range(1, len(kernel_logs) - 2, 4):
        if random.random() > 0.5:
            kernel_logs[i], kernel_logs[i+1] = kernel_logs[i+1], kernel_logs[i]

    # 写入文件
    with open("logs/trace_pipe.log", "w", encoding="utf-8") as f:
        f.write("# tracer: nop\n#\n")
        f.write("# entries-in-buffer/entries-written: 1024/1024   #P:8\n#\n")
        f.write("#                              _-----=> irqs-off\n")
        f.write("#                             / _----=> need-resched\n")
        f.write("#                            | / _---=> hardirq/softirq\n")
        f.write("#                            || / _--=> preempt-depth\n")
        f.write("#                            ||| /     delay\n")
        f.write("#           TASK-PID   CPU#  ||||    TIMESTAMP  FUNCTION\n")
        f.write("#              | |       |   ||||       |         |\n")
        f.write("\n".join(kernel_logs))

    # 生成供工具内部查询使用的真实数据源（隐藏文件，不可见/不易被直读）
    with open("pcap_export/.siem_backend_db.json", "w", encoding="utf-8") as f:
        json.dump(siem_backend_data, f)

    # 制造一份已加密的乱码占位文件，彻底断绝强行文本读取的希望
    with open("pcap_export/traffic_capture.pcap.enc", "wb") as f:
        f.write(os.urandom(2048))
        f.write(b"==== SECURE ENCRYPTED PAYLOAD ====")
        f.write(os.urandom(2048))

if __name__ == "__main__":
    build_env()
