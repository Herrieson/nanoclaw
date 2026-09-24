import os
import random
import time

def build_env():
    # 创建所需目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("pcap_export", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    # 预设各种 IP 和其状态
    # 为了保证可评测性，我们固定几个会触发 ERR_MALFORMED 的恶毒 IP
    malformed_ips = ["120.44.55.66", "45.33.22.11", "10.0.5.200"]
    rate_limit_ips = ["192.168.1.50", "172.16.0.12"]
    normal_ips = ["8.8.8.8", "1.1.1.1", "10.10.10.10", "192.168.100.1"]

    kernel_logs = []
    pcap_dumps = []

    # 制造大量杂乱的内核调度/中断日志作为干扰
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
        # 增加一些时间步进
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
        
        # 制造内核日志乱码干扰（故意混入带非ASCII的截断打印）
        if random.random() > 0.8:
            kernel_logs.append(f"bpf_trace_printk: [TRUNCATED] \xDE\xAD\xBE\xEF buffer full at {t_str}")
            
        kernel_logs.append(log_line)

        # 生成 pcap text dump 格式 (非标准结构，模拟极其粗糙的脚本提取)
        hex_dump = " ".join([f"{random.randint(0, 255):02X}" for _ in range(random.randint(16, 32))])
        dst_ip = f"10.200.0.{random.randint(1, 254)}"
        
        # 故意让格式稍微有点脏乱，测试正则或解析逻辑的鲁棒性
        spaces = " " * random.randint(1, 4)
        dump_entry = f"""==== PKT_START ====
T:{base_time:.6f}
  ID:{spaces}{pkt_id}
> NET_L3: SRC={pkt["ip"]}{spaces}| DST={dst_ip}
    HEX_PREVIEW:{hex_dump}
==== PKT_END ====
"""
        pcap_dumps.append(dump_entry)

    # 写入内核日志，故意打乱部分日志的顺序，模拟SMP下的真实输出乱序
    # (仅微调附近几行的顺序)
    for i in range(1, len(kernel_logs) - 2, 4):
        if random.random() > 0.5:
            kernel_logs[i], kernel_logs[i+1] = kernel_logs[i+1], kernel_logs[i]

    with open("logs/trace_pipe.log", "w", encoding="utf-8") as f:
        # 加个假的头部
        f.write("# tracer: nop\n")
        f.write("#\n")
        f.write("# entries-in-buffer/entries-written: 1024/1024   #P:8\n")
        f.write("#\n")
        f.write("#                              _-----=> irqs-off\n")
        f.write("#                             / _----=> need-resched\n")
        f.write("#                            | / _---=> hardirq/softirq\n")
        f.write("#                            || / _--=> preempt-depth\n")
        f.write("#                            ||| /     delay\n")
        f.write("#           TASK-PID   CPU#  ||||    TIMESTAMP  FUNCTION\n")
        f.write("#              | |       |   ||||       |         |\n")
        f.write("\n".join(kernel_logs))

    with open("pcap_export/tcpdump_raw.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(pcap_dumps))

if __name__ == "__main__":
    build_env()
