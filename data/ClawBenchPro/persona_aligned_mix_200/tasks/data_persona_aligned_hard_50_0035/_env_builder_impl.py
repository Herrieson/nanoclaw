import os
import random
import string
import json
from datetime import datetime, timedelta

def generate_random_hex(prefix="0x7f"):
    return prefix + "".join(random.choices(string.hexdigits.lower(), k=10))

def generate_vertex_id():
    return f"V_0x{random.randint(1000, 9999):04x}_{random.randint(10000, 99999)}"

def generate_task_id():
    return f"TASK_{random.randint(100000, 999999)}"

def build_env():
    # 建立目录结构
    os.makedirs("coordinator", exist_ok=True)
    os.makedirs("router", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("hotfix", exist_ok=True)

    # 预设真理数据（唯一正解）
    TARGET_SUPERNODE = "V_0xdead_66666"
    TARGET_TASK_ID = "TASK_888888"
    TARGET_WORKER_IP = "10.0.5.55"
    TARGET_LEAK_ADDR = "0x7fa1b2c3d4e5"

    # 预设陷阱数据 1：发生溢出，但最终没形成真正的环（未打爆内存）
    DECOY1_SUPERNODE = "V_0xbeef_11111"
    DECOY1_TASK_ID = "TASK_111111"
    DECOY1_WORKER_IP = "10.0.2.22"

    # 预设陷阱数据 2：有真实的内存环形引用，但并不是溢出任务导致的（常态内存驻留）
    DECOY2_SUPERNODE = "V_0xcafe_22222"
    DECOY2_TASK_ID = "TASK_222222"
    DECOY2_WORKER_IP = "10.0.8.88"
    DECOY2_LEAK_ADDR = "0x7f9999999999"

    workers = [f"10.0.{i}.{i*11}" for i in range(1, 10)]

    # ==========================================
    # 1. 构建 Coordinator 日志 (极度碎片化，包含大量分片)
    # ==========================================
    base_time = datetime(2023, 10, 27, 3, 0, 0)
    
    for shard in range(20):
        os.makedirs(f"coordinator/shard_{shard:02d}", exist_ok=True)
        for f_idx in range(5):
            with open(f"coordinator/shard_{shard:02d}/frag_{f_idx}.log", "w") as f:
                for line in range(200):
                    t = base_time + timedelta(seconds=random.randint(0, 3600))
                    task_id = generate_task_id()
                    v_id = generate_vertex_id()
                    state = random.choice(["FRAG_OK", "FRAG_PENDING", "FRAG_RETRY"])
                    
                    # 植入目标和陷阱
                    if shard == 7 and f_idx == 3 and line == 115:
                        task_id, v_id, state = TARGET_TASK_ID, TARGET_SUPERNODE, "FRAG_SPLIT_OVERFLOW"
                    elif shard == 14 and f_idx == 1 and line == 42:
                        task_id, v_id, state = DECOY1_TASK_ID, DECOY1_SUPERNODE, "FRAG_SPLIT_OVERFLOW"
                    elif shard == 2 and f_idx == 4 and line == 88:
                        task_id, v_id, state = DECOY2_TASK_ID, DECOY2_SUPERNODE, "FRAG_OK" # 没有溢出
                        
                    f.write(f"[{t.strftime('%H:%M:%S.%f')}] [{task_id}] EXECUTOR: expand_vertex_op | node_id: {v_id} | state: {state}\n")

    # ==========================================
    # 2. 构建 Router 历史路由表 (追踪任务去向)
    # ==========================================
    routing_records = []
    for _ in range(500):
        routing_records.append({
            "task_id": generate_task_id(),
            "dispatched_to": random.choice(workers),
            "timestamp": (base_time + timedelta(seconds=random.randint(0, 3600))).isoformat()
        })
    
    # 植入关键路由信息
    routing_records.append({"task_id": TARGET_TASK_ID, "dispatched_to": TARGET_WORKER_IP, "timestamp": base_time.isoformat()})
    routing_records.append({"task_id": DECOY1_TASK_ID, "dispatched_to": DECOY1_WORKER_IP, "timestamp": base_time.isoformat()})
    routing_records.append({"task_id": DECOY2_TASK_ID, "dispatched_to": DECOY2_WORKER_IP, "timestamp": base_time.isoformat()})
    
    random.shuffle(routing_records)
    
    # 将路由记录打碎成多个 JSON 文件
    chunk_size = len(routing_records) // 8
    for i in range(8):
        with open(f"router/history_chunk_{i}.json", "w") as f:
            json.dump({"routes": routing_records[i*chunk_size : (i+1)*chunk_size]}, f, indent=2)

    # ==========================================
    # 3. 构建 Worker Dumps (包含隐藏的真正环形引用和大量假链)
    # ==========================================
    for worker in workers:
        worker_dir = f"dumps/worker_{worker}"
        os.makedirs(worker_dir, exist_ok=True)
        
        for dump_idx in range(4):
            with open(f"{worker_dir}/heap_trace_{dump_idx}.dump", "w") as f:
                f.write(f"--- HEAP TRACE DUMP FOR {worker} ---\n")
                
                for entry in range(150):
                    addr_start = generate_random_hex()
                    addr_mid = generate_random_hex()
                    addr_end = generate_random_hex()
                    
                    chain = f"{addr_start} -> {addr_mid} -> {addr_end} -> NULL"
                    ctx_task = generate_task_id()
                    ctx_node = generate_vertex_id()
                    
                    # 植入唯一真解
                    if worker == TARGET_WORKER_IP and dump_idx == 2 and entry == 77:
                        ctx_task = TARGET_TASK_ID
                        ctx_node = TARGET_SUPERNODE
                        chain = f"{TARGET_LEAK_ADDR} -> {generate_random_hex()} -> {generate_random_hex()} -> {generate_random_hex()} -> {TARGET_LEAK_ADDR}"
                    
                    # 植入陷阱1: 是溢出任务，但是内存没闭环
                    elif worker == DECOY1_WORKER_IP and dump_idx == 1 and entry == 30:
                        ctx_task = DECOY1_TASK_ID
                        ctx_node = DECOY1_SUPERNODE
                        chain = f"{addr_start} -> {addr_mid} -> {addr_end} -> {generate_random_hex()} -> NULL"
                        
                    # 植入陷阱2: 形成闭环，但其任务根本没发生溢出（属于干扰环）
                    elif worker == DECOY2_WORKER_IP and dump_idx == 3 and entry == 110:
                        ctx_task = DECOY2_TASK_ID
                        ctx_node = DECOY2_SUPERNODE
                        chain = f"{DECOY2_LEAK_ADDR} -> {generate_random_hex()} -> {DECOY2_LEAK_ADDR}"
                    
                    # 随机制造一些看似像环，其实头尾差了一个字符的假数据
                    elif random.random() < 0.05:
                        fake_start = "0x7fa1b2c3d4e0"
                        fake_end = "0x7fa1b2c3d4e1" # 尾号不同
                        chain = f"{fake_start} -> {generate_random_hex()} -> {fake_end}"
                        
                    f.write(f"Allocated: {random.choice([256, 1024, 4096, 8192])} bytes\n")
                    f.write(f"Context: Task={ctx_task} Node={ctx_node}\n")
                    f.write(f"RawHex: {''.join(random.choices(string.hexdigits.lower(), k=64))}\n")
                    f.write(f"RefChain: {chain}\n")
                    f.write("----------------------------------------\n")

if __name__ == "__main__":
    build_env()
