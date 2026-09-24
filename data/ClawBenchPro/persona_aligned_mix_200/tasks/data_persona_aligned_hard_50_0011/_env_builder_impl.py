import os
import random
import json
import uuid

def build_env():
    os.makedirs("telemetry_shards", exist_ok=True)
    os.makedirs("pg_stat_activity", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("interference_logs", exist_ok=True)

    # 全局数据池
    sessions = []
    edges = []  # (waiter_pid, holder_pid)

    def generate_pid():
        return random.randint(100000, 999999)

    def generate_xid():
        return random.randint(10000000, 99999999)

    # ==========================================
    # 1. 构建唯一的罪魁祸首与史诗级大雪崩 (Root Blocker)
    # ==========================================
    root_pid = generate_pid()
    root_xid = generate_xid()
    
    sessions.append({
        "pid": root_pid, "user": "core_admin", "xid": root_xid, 
        "query": "UPDATE orders SET status='LOCKED' WHERE is_active = true;"
    })

    # 生成大规模多级等待树
    current_level_holders = [root_pid]
    avalanche_size = 800
    generated_count = 0
    
    while generated_count < avalanche_size:
        next_level_holders = []
        # 每层衍生 2~5 个子节点
        for holder in current_level_holders:
            num_children = random.randint(2, 5)
            for _ in range(num_children):
                if generated_count >= avalanche_size:
                    break
                waiter_pid = generate_pid()
                sessions.append({
                    "pid": waiter_pid, "user": "app_client", "xid": generate_xid(),
                    "query": f"SELECT * FROM orders WHERE id = {random.randint(1,1000)} FOR UPDATE;"
                })
                edges.append((waiter_pid, holder))
                next_level_holders.append(waiter_pid)
                generated_count += 1
        current_level_holders = next_level_holders
        if not current_level_holders:
            break

    # ==========================================
    # 2. 构建若干个小规模的干扰阻塞链
    # ==========================================
    for _ in range(5):
        minor_root_pid = generate_pid()
        sessions.append({
            "pid": minor_root_pid, "user": "bg_worker", "xid": generate_xid(), 
            "query": "DELETE FROM temp_logs;"
        })
        current_minor = minor_root_pid
        for _ in range(random.randint(5, 15)):
            w_pid = generate_pid()
            sessions.append({
                "pid": w_pid, "user": "bg_worker", "xid": generate_xid(), 
                "query": "INSERT INTO temp_logs VALUES (...);"
            })
            edges.append((w_pid, current_minor))
            current_minor = w_pid

    # ==========================================
    # 3. 构建死锁环 (极其重要的干扰，测试 Agent 的图算法健壮性)
    # ==========================================
    for _ in range(3):
        ring_pids = [generate_pid() for _ in range(random.randint(3, 6))]
        for p in ring_pids:
            sessions.append({
                "pid": p, "user": "deadlock_maker", "xid": generate_xid(), 
                "query": "UPDATE account SET balance = balance - 1;"
            })
        for i in range(len(ring_pids)):
            w = ring_pids[i]
            h = ring_pids[(i + 1) % len(ring_pids)]
            edges.append((w, h))

    # 加入大量无关的空闲 session
    for _ in range(500):
        sessions.append({
            "pid": generate_pid(), "user": "idle_user", "xid": "None", 
            "query": "COMMIT;"
        })

    # ==========================================
    # 数据碎片化写入
    # ==========================================
    
    # 打乱所有数据
    random.shuffle(sessions)
    random.shuffle(edges)

    # 碎片化 telemetry (边信息)
    num_telemetry_files = 30
    telemetry_dirs = [f"telemetry_shards/node_{i}" for i in range(5)]
    for d in telemetry_dirs:
        os.makedirs(d, exist_ok=True)
        
    for i in range(num_telemetry_files):
        target_dir = random.choice(telemetry_dirs)
        with open(os.path.join(target_dir, f"trace_dump_{uuid.uuid4().hex[:8]}.log"), "w") as f:
            lines = []
            for _ in range(random.randint(20, 50)):
                # 注入大量垃圾系统日志
                lines.append(f"[{uuid.uuid4().hex[:8]}] INFO: Metric check passed, load={random.uniform(0, 10):.2f}")
            
            # 分配一批边到这个文件中
            chunk_size = len(edges) // num_telemetry_files + 1
            chunk_edges = edges[i * chunk_size : (i + 1) * chunk_size]
            for w, h in chunk_edges:
                hex_w = hex(w)
                hex_h = hex(h)
                noise_prefix = f"[{random.choice(['CRIT', 'WARN', 'ERROR'])}] PG_LOCK_MONITOR: "
                # 核心特征模式： [w: <hex_pid>] is blocked by [h: <hex_pid>]
                lines.append(f"{noise_prefix} Wait dependency detected: [w: {hex_w}] is blocked by [h: {hex_h}] due to ExclusiveLock.")
                # 再掺杂点日志
                if random.random() > 0.7:
                    lines.append(f"[{uuid.uuid4().hex[:8]}] DEBUG: Cache miss for id {random.randint(1,100)}")
            
            random.shuffle(lines)
            f.write("\n".join(lines) + "\n")

    # 碎片化 pg_stat_activity (节点信息)
    num_pg_files = 20
    for i in range(num_pg_files):
        with open(os.path.join("pg_stat_activity", f"snapshot_{random.randint(1000,9999)}.dat"), "w") as f:
            chunk_size = len(sessions) // num_pg_files + 1
            chunk_sess = sessions[i * chunk_size : (i + 1) * chunk_size]
            lines = ["# PROBE DUMP v2.1.0", "# FORMAT: TIMESTAMP || PID:<dec> || USER:<str> || XID:<dec> || Q:<str>"]
            for s in chunk_sess:
                # 混淆格式，自定义分隔符
                ts = f"2023-11-01T03:14:{random.randint(10,59)}Z"
                lines.append(f"RECORD | {ts} || PID:{s['pid']} || USER:{s['user']} || XID:{s['xid']} || Q:{s['query']}")
            f.write("\n".join(lines) + "\n")

    # 制造纯干扰文件（混淆视听）
    with open("interference_logs/legacy_deadlock.log", "w") as f:
        f.write("PG_LOCK_MONITOR: Wait dependency detected: [w: 0x9999] is blocked by [h: 0x8888] due to ExclusiveLock.\n")
        f.write("PG_LOCK_MONITOR: Wait dependency detected: [w: 0x8888] is blocked by [h: 0x9999] due to ExclusiveLock.\n")
        f.write("THIS FILE IS OUTDATED. DO NOT USE.\n")
