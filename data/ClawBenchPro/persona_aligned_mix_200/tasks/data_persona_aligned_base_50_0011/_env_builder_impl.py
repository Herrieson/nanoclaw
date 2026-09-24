import os
import random
import json

def build_env():
    # 确保在当前环境(即 assets/data_persona_aligned_base_50_0011/) 下创建目录结构
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("interference", exist_ok=True)

    # 罪魁祸首：Root Blocker
    root_pid = 14920
    root_xid = 9948271

    # 雪崩等待队列
    l1_waiters = [15000 + i for i in range(12)]
    l2_waiters = [16000 + i for i in range(25)]
    idle_pids = [11000 + i for i in range(40)]

    # 孤立的干扰等待 (不构成大面积雪崩)
    isolated_holder = 7777
    isolated_holder_xid = 8881112
    isolated_waiter = 7778

    sessions = []
    
    # 注入 root blocker
    sessions.append((
        root_pid, 
        'app_admin', 
        'active', 
        root_xid, 
        "UPDATE core_inventory SET stock_count = stock_count - 10000 WHERE sku_id = 'FLASH_SALE_001';"
    ))
    
    # 注入孤立干扰项
    sessions.append((
        isolated_holder, 
        'cron_user', 
        'idle in transaction', 
        isolated_holder_xid, 
        "DELETE FROM audit_logs WHERE created_at < '2022-01-01';"
    ))
    sessions.append((
        isolated_waiter, 
        'cron_user', 
        'active', 
        isolated_holder_xid + 1, 
        "UPDATE audit_logs SET status = 'archived';"
    ))

    # 注入 L1 Waiters
    for pid in l1_waiters:
        sessions.append((
            pid, 
            'app_client', 
            'active', 
            root_xid + random.randint(10, 100), 
            "UPDATE core_inventory SET stock_count = stock_count - 1 WHERE sku_id = 'FLASH_SALE_001';"
        ))
        
    # 注入 L2 Waiters
    for pid in l2_waiters:
        wait_on = random.choice(l1_waiters)
        sessions.append((
            pid, 
            'app_client', 
            'active', 
            root_xid + random.randint(100, 200), 
            f"SELECT stock_count FROM core_inventory WHERE sku_id = 'FLASH_SALE_001' FOR UPDATE;"
        ))
        
    # 注入空闲会话
    for pid in idle_pids:
        sessions.append((
            pid, 
            'readonly_user', 
            'idle', 
            'NULL', 
            "SELECT 1;"
        ))

    random.shuffle(sessions)

    out_lines = []
    out_lines.append("=== POSTGRES RAW CRASH DUMP ===")
    out_lines.append("TIMESTAMP: 2023-11-01T03:14:02Z")
    out_lines.append("SYS_LOAD: 128.45 110.22 89.10")
    out_lines.append("===============================\n")

    # 构建非标准分隔符的会话快照
    out_lines.append("--- SESSION SNAPSHOT ---")
    out_lines.append("FORMAT: session_id~!~db_user~!~txn_state~!~backend_xid~!~current_query")
    for s in sessions:
        out_lines.append(f"{s[0]}~!~{s[1]}~!~{s[2]}~!~{s[3]}~!~{s[4]}")

    # 构建混淆了十六进制 PID 的锁依赖图
    out_lines.append("\n--- LOCK DEPENDENCY GRAPH ---")
    out_lines.append("FORMAT: [Waiter: <hex_pid>] is blocked by [Holder: <hex_pid>] via <LockType>")
    
    edges = []
    # 干扰等待边
    edges.append((isolated_waiter, isolated_holder, "AccessExclusiveLock"))
    
    # 主雪崩等待边
    for pid in l1_waiters:
        edges.append((pid, root_pid, "RowExclusiveLock"))
    for pid in l2_waiters:
        edges.append((pid, random.choice(l1_waiters), "ShareLock"))

    random.shuffle(edges)
    for w, h, lock_type in edges:
        out_lines.append(f"[Waiter: {hex(w)}] is blocked by [Holder: {hex(h)}] via {lock_type}")

    # 加入冗长的假 EXPLAIN JSON 制造上下文噪声
    out_lines.append("\n--- EXPLAIN ANALYZE SNIPPETS ---")
    noise_plan = {
        "Plan": {
            "Node Type": "Hash Join",
            "Parallel Aware": False,
            "Async Capable": False,
            "Join Type": "Inner",
            "Startup Cost": 1234.56,
            "Total Cost": 98765.43,
            "Plan Rows": 15000000,
            "Plan Width": 256,
            "Actual Total Time": 34502.1,
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Parent Relationship": "Outer",
                    "Relation Name": "core_inventory",
                    "Alias": "ci"
                }
            ]
        }
    }
    out_lines.append(json.dumps(noise_plan, indent=2))
    out_lines.append("WARN: pg_stat_statements limits exceeded. Some query texts truncated.")

    # 写入诊断输出
    with open("db_dumps/crash_state.out", "w") as f:
        f.write("\n".join(out_lines))

    # 生成一些干扰文件
    with open("interference/redis_slowlog.txt", "w") as f:
        f.write("1) (integer) 14\n2) (integer) 1609459200\n3) (integer) 25000\n4) 1) \"KEYS\"\n   2) \"*\"\n")
    with open("interference/dmesg_tail.log", "w") as f:
        f.write("[12345.678901] Out of memory: Killed process 888 (python3) total-vm:458900kB, anon-rss:210400kB\n")
