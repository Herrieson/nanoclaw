import os
import argparse
import random
import json

def build_turn_1():
    random.seed(42)
    os.makedirs("traffic_dumps", exist_ok=True)
    os.makedirs("bpf_traces", exist_ok=True)
    
    with open("traffic_dumps/dump_A.log", "w") as f_dump, \
         open("bpf_traces/trace.log", "w") as f_trace:
        
        f_dump.write("TIMESTAMP | SRC_IP:SRC_PORT -> DST_IP:DST_PORT | PROTO | LEN\n")
        
        events = []
        
        # 干扰项：正常流量混杂着无关的限流丢包 (reason 0A, map 50)
        for i in range(100):
            ts = 1600000000.0 + i * 0.5
            src = f"192.168.1.{random.randint(1, 250)}"
            dst = f"10.0.0.{random.randint(1, 10)}"
            port = random.choice([80, 443, 22])
            length = random.randint(64, 1000)
            events.append((ts, f"{ts:.2f} | {src}:{random.randint(10000, 60000)} -> {dst}:{port} | TCP | {length}\n"))
            
            if random.random() < 0.1:
                events.append((ts, f"[{ts:.2f}] bpf_trace_printk: [xdp_filter] DROP src={src} reason=0A map=50\n", "trace"))
                
        # 目标 Bug 流量：特定网段、特定端口、长度超标 (reason 1B, map 105)
        for i in range(40):
            ts = 1600000010.0 + i * 1.2
            src = f"10.10.1.{random.randint(10, 200)}"
            dst = "10.20.30.40"
            port = 8443
            length = random.randint(1501, 2000)
            events.append((ts, f"{ts:.2f} | {src}:{random.randint(10000, 60000)} -> {dst}:{port} | TCP | {length}\n"))
            events.append((ts, f"[{ts:.2f}] bpf_trace_printk: [xdp_filter] DROP src={src} reason=1B map=105\n", "trace"))

        # 目标网段的正常流量：长度未超标，不触发丢包
        for i in range(40):
            ts = 1600000015.0 + i * 1.2
            src = f"10.10.1.{random.randint(10, 200)}"
            dst = "10.20.30.40"
            port = 8443
            length = random.randint(500, 1500)
            events.append((ts, f"{ts:.2f} | {src}:{random.randint(10000, 60000)} -> {dst}:{port} | TCP | {length}\n"))
            
        events.sort(key=lambda x: x[0])
        
        for ev in events:
            if len(ev) == 2:
                f_dump.write(ev[1])
            else:
                f_trace.write(ev[1])

def build_turn_2():
    random.seed(142)
    os.makedirs("new_incoming_traffic", exist_ok=True)
    os.makedirs("hardware_config", exist_ok=True)
    os.makedirs("alerts", exist_ok=True)
    
    cpu_map = {}
    with open("new_incoming_traffic/batch2.log", "w") as f_dump:
        f_dump.write("TIMESTAMP | SRC_IP:SRC_PORT -> DST_IP:DST_PORT | PROTO | LEN\n")
        
        for i in range(150):
            ts = 1600000500.0 + i * 0.5
            if random.random() < 0.5:
                # 潜在的 Bug 网段，长度随机，Agent需要自己判断是否 > 1500
                src = f"10.10.1.{random.randint(10, 250)}"
                dst = "10.20.30.40"
                port = 8443
                length = random.randint(1000, 2000)
            else:
                # 干扰网段
                src = f"192.168.5.{random.randint(1, 200)}"
                dst = "10.0.0.1"
                port = 80
                length = random.randint(64, 1500)
                
            f_dump.write(f"{ts:.2f} | {src}:{random.randint(10000, 60000)} -> {dst}:{port} | TCP | {length}\n")
            
            if src not in cpu_map:
                cpu_map[src] = f"CPU-{random.randint(0, 7)}"
                
    with open("hardware_config/rx_queues.json", "w") as f_cpu:
        json.dump(cpu_map, f_cpu, indent=2)

def build_turn_3():
    random.seed(242)
    os.makedirs("sec_ops", exist_ok=True)
    
    # CIDR 陷阱：仅放行后半段 IP，前半段仍在黑名单中
    whitelist = {
        "exempt_subnets": ["10.10.1.128/25"],
        "exempt_ports": [8443],
        "note": "Any source IP matching the exempt_subnets must be unconditionally bypassed, regardless of length."
    }
    with open("sec_ops/emergency_whitelist.json", "w") as f:
        json.dump(whitelist, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
