import os
import random
import string
from datetime import datetime, timedelta

def generate_random_hex():
    return "0x" + "".join(random.choices(string.hexdigits.lower(), k=12))

def generate_vertex_id():
    return f"V_0x{random.randint(1000, 9999):04x}_{random.randint(10000, 99999)}"

def build_env():
    # 建立目录结构（纯相对路径）
    os.makedirs("coordinator", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("hotfix", exist_ok=True)

    # 预定义关键的超级节点和泄漏地址
    supernode_id = "V_0x8f9e_77b21"
    leak_address = "0x7fa1b2c4e000"

    # ==========================================
    # 1. 生成 Coordinator 的查询计划碎片日志
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
    # 2. 生成 Worker 节点的内存分配堆栈日志 (带乱码和脏数据)
    # ==========================================
    with open("dumps/worker_alloc_heap.trace", "w", encoding="utf-8") as f:
        f.write("HEAP_ALLOCATION_TRACE_DUMP v2.1.4\n")
        f.write("WARN: Trace contains raw hex dumps and unregistered pointers.\n")
        f.write("=" * 60 + "\n")
        
        for i in range(2000):
            alloc_addr = generate_random_hex()
            size = random.choice([64, 128, 256, 1024, 4096])
            
            # 随机生成正常的分配链
            chain = f"{alloc_addr} -> {generate_random_hex()} -> NULL"
            context_v_id = generate_vertex_id()
            
            if i == 1672:
                # 植入目标：超级节点的环形引用
                alloc_addr = leak_address
                context_v_id = supernode_id
                size = 1048576 * 100 # 巨大的分配
                mid_addr_1 = generate_random_hex()
                mid_addr_2 = generate_random_hex()
                chain = f"{alloc_addr} -> {mid_addr_1} -> {mid_addr_2} -> {alloc_addr} (CIRCULAR_DETECTED)"

            f.write(f"Alloc: {size} bytes @ {alloc_addr}\n")
            f.write(f"Context: expand_vertex [{context_v_id}]\n")
            
            # 生成随机的 16 进制脏乱码模拟底层内存快照
            f.write("RawDump: ")
            f.write(" ".join(random.choices(string.hexdigits.lower(), k=32)) + "...\n")
            
            f.write(f"RefChain: {chain}\n")
            f.write("-" * 30 + "\n")
            
    # ==========================================
    # 3. 生成一些噪音文件增加难度
    # ==========================================
    with open("dumps/worker_01_health.log", "w", encoding="utf-8") as f:
        f.write("NODE_HEALTH_OK\nCPU: 12%\nMEM: 8%\n")
        
    with open("coordinator/schema_meta.dat", "wb") as f:
        # 写入随机字节流作为二进制噪音文件
        f.write(os.urandom(2048))

if __name__ == "__main__":
    build_env()
