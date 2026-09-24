import os
import random
import string
import json
from datetime import datetime, timedelta

def generate_vertex_id():
    return f"V_0x{random.randint(1000, 9999):04x}_{random.randint(10000, 99999)}"

def build_env():
    # 建立目录结构（纯相对路径）
    os.makedirs("coordinator", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("hotfix", exist_ok=True)

    # 预定义关键的超级节点和泄漏地址（作为 Ground Truth）
    supernode_id = "V_0x8f9e_77b21"
    leak_address = "0x7fa1b2c4e000"

    # 将 Ground Truth 写入隐藏的 meta 文件，供 Mock API 读取
    with open(".hidden_meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "supernode_id": supernode_id,
            "leak_address": leak_address
        }, f)

    # ==========================================
    # 1. 生成 Coordinator 的查询计划碎片明文日志
    # ==========================================
    start_time = datetime.now() - timedelta(hours=2)
    with open("coordinator/plan_fragments_171092.log", "w", encoding="utf-8") as f:
        f.write("=== GRAPH_DB_COORDINATOR_QUERY_PLAN_DUMP ===\n")
        f.write("CLUSTER_STATE: DEGRADED\n")
        
        for i in range(1500):
            t = start_time + timedelta(milliseconds=i*15)
            frag_id = f"FRAG_{random.randint(100000, 999999)}"
            v_id = generate_vertex_id()
            degree = random.randint(1, 50)
            state = "FRAG_OK"
            
            # 混入超级节点导致溢出的日志
            if i == 1134:
                v_id = supernode_id
                degree = 18492041 # 极度夸张的度数
                state = "FRAG_SPLIT_OVERFLOW"
                
            log_line = f"[{t.isoformat()}] [{frag_id}] expand_vertex: {v_id} | degree: {degree} | state: {state}\n"
            f.write(log_line)
            
            # 干扰项
            if i % 100 == 0:
                f.write(f"[{t.isoformat()}] [SYSTEM] GC triggered. Memory usage at {random.randint(40, 60)}%\n")

    # ==========================================
    # 2. 改造点：将原本明文的 worker trace 变为完全不可直接读取的二进制 Dump
    # ==========================================
    with open("dumps/worker_alloc_heap.core", "wb") as f:
        # 写入 ELF 魔法头，并填充 5MB 的纯随机二进制脏数据，模拟真实 core 文件
        f.write(b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        f.write(os.urandom(1024 * 1024 * 5))
            
    # ==========================================
    # 3. 生成一些噪音文件增加难度
    # ==========================================
    with open("dumps/worker_01_health.log", "w", encoding="utf-8") as f:
        f.write("NODE_HEALTH_OK\nCPU: 12%\nMEM: 99%\nFATAL: OOM_KILLED\n")

if __name__ == "__main__":
    build_env()
