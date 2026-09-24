import os
import json
import random

def build_env():
    # 创建所需的工作目录，此时 cwd 已经是 assets/data_persona_aligned_base_50_0050/
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 构造深层嵌套的死锁等待依赖图谱 (JSON格式)
    # 逻辑：11021 是根源阻塞者，它阻塞了 11055 和 11099，引发了后续的一系列阻塞，而 11021 自己没有被任何人阻塞。
    deadlock_data = {
        "cluster": {
            "name": "prod-pg-main",
            "status": "degraded",
            "diagnostics": {
                "lock_manager": {
                    "cycle_detected": True,
                    "resolution_in_progress": False,
                    "wait_edges": [
                        {"waiter_pid": 11055, "blocking_pid": 11021, "lock_mode": "ShareLock", "relation": "orders"},
                        {"waiter_pid": 11099, "blocking_pid": 11021, "lock_mode": "ExclusiveLock", "relation": "orders"},
                        {"waiter_pid": 12001, "blocking_pid": 11099, "lock_mode": "ShareLock", "relation": "inventory"},
                        {"waiter_pid": 12055, "blocking_pid": 12001, "lock_mode": "ExclusiveLock", "relation": "users"},
                        {"waiter_pid": 8832,  "blocking_pid": 11055, "lock_mode": "ShareLock", "relation": "orders"}
                    ],
                    "memory_context": "0x7f8b9c000000"
                }
            }
        }
    }

    with open("db_dumps/deadlock_detector_out.json", "w", encoding="utf-8") as f:
        json.dump(deadlock_data, f, indent=2)

    # 2. 构造非标准格式的活动快照文本 (带有诡异的分隔符和脏数据)
    snapshot_lines = [
        "TIME_STAMP @@ {PID} @@ STATE @@ XID_HEX @@ QUERY_SNIPPET",
        "2023-10-27T03:00:12Z @@ {8832} @@ active @@ 0x8F400 @@ SELECT * FROM users WHERE active = true;",
        "2023-10-27T03:00:13Z @@ {11055} @@ active @@ 0x8F412 @@ UPDATE orders SET status = 'DONE' WHERE id IN (SELECT id FROM unproc);",
        "2023-10-27T03:00:14Z @@ {11099} @@ active @@ 0x8F415 @@ DELETE FROM orders WHERE status = 'PROCESSING';",
        "2023-10-27T03:00:15Z @@ {11021} @@ idle in transaction @@ 0xDEADBEEF @@ BEGIN; UPDATE orders SET status = 'PROCESSING' WHERE id = 99281; -- DBA note: left console open!",
        "2023-10-27T03:00:16Z @@ {12001} @@ active @@ 0x8F419 @@ INSERT INTO orders_log VALUES (1, 'WAITING');",
        "2023-10-27T03:00:17Z @@ {12055} @@ active @@ 0x8F42A @@ VACUUM ANALYZE orders;"
    ]
    
    header = snapshot_lines[0]
    data_lines = snapshot_lines[1:]
    # 打乱数据行以增加查找难度
    random.seed(77)
    random.shuffle(data_lines)

    with open("db_dumps/activity_snapshot_0300.raw", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(data_lines) + "\n")

    # 3. 构造充满干扰信息和乱码的 EXPLAIN ANALYZE 日志
    explain_content = """
[PLAN NODE 0x00A1F] -> Seq Scan on orders (cost=0.00..12543.00 rows=1000 width=12) (actual time=0.012..45.123 rows=1 loops=1)
    Filter: (status = 'PROCESSING'::text)
    Rows Removed by Filter: 999999
    Buffers: shared hit=15 read=105 dirtied=1
[PLAN NODE 0x00B22] -> LockRows (cost=12543.00..12553.00 rows=1000 width=12) (actual time=45.125..45.125 rows=1 loops=1)
>> MEMORY CONTEXT: 0x7f8b9c000000 (AllocSet)
>> LOCK WAIT: tuple (16552, 4, 15) in ExclusiveMode
01010100 01110010 01100001 01101110 01110011 01100001 01100011 01110100 01101001 01101111 01101110 00100000 01101000 01110101 01101110 01100111
WARN: deadlock detected in LWLockAcquire
DETAIL: Process 11055 waits for ShareLock on transaction 11021; blocked by process 11021.
HINT: See server log for query details.
\x00\x00\x00\x1F\x8B\x08\x00\x00\x00\x00\x00\x00\x03\x00 (Corrupted buffer tail)
    """
    
    with open("db_dumps/explain_analyze_garbage.log", "w", encoding="utf-8") as f:
        f.write(explain_content)
