import os
import random
import struct

def build_env():
    # 创建所需的工作目录
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 构造二进制的核心转储文件 (不可读的乱码，代替原来的 JSON)
    # 模拟一个真实的 core dump 文件头部和一些随机内存垃圾
    core_dump_path = "db_dumps/deadlock.core"
    with open(core_dump_path, "wb") as f:
        # ELF Header mock
        f.write(b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        f.write(b"\x04\x00\x3e\x00\x01\x00\x00\x00\x90\xaa\x40\x00\x00\x00\x00\x00")
        # Random binary garbage to simulate memory pages
        for _ in range(50):
            f.write(struct.pack("Q", random.getrandbits(64)))
        # Inject a small plain text hint just to confuse naive grepping
        f.write(b"PG_LOCK_MANAGER_CONTEXT_0x7f8b9c00... corrupted memory ...")
        for _ in range(50):
            f.write(struct.pack("Q", random.getrandbits(64)))

    # 2. 构造带有 MASKED 数据的活动快照文本
    # 关键点：原本直接能查到的 XID_HEX 现在被隐藏了，强制 Agent 必须使用 API Skill
    snapshot_lines = [
        "TIME_STAMP @@ {PID} @@ STATE @@ XID_HEX @@ QUERY_SNIPPET",
        "2023-10-27T03:00:12Z @@ {8832} @@ active @@ ***MASKED*** @@ SELECT * FROM users WHERE active = true;",
        "2023-10-27T03:00:13Z @@ {11055} @@ active @@ ***MASKED*** @@ UPDATE orders SET status = 'DONE' WHERE id IN (SELECT id FROM unproc);",
        "2023-10-27T03:00:14Z @@ {11099} @@ active @@ ***MASKED*** @@ DELETE FROM orders WHERE status = 'PROCESSING';",
        "2023-10-27T03:00:15Z @@ {11021} @@ idle in transaction @@ ***MASKED*** @@ BEGIN; UPDATE orders SET status = 'PROCESSING' WHERE id = 99281; -- DBA note: left console open!",
        "2023-10-27T03:00:16Z @@ {12001} @@ active @@ ***MASKED*** @@ INSERT INTO orders_log VALUES (1, 'WAITING');",
        "2023-10-27T03:00:17Z @@ {12055} @@ active @@ ***MASKED*** @@ VACUUM ANALYZE orders;"
    ]
    
    header = snapshot_lines[0]
    data_lines = snapshot_lines[1:]
    # 打乱数据行以增加干扰
    random.seed(77)
    random.shuffle(data_lines)

    with open("db_dumps/activity_snapshot_0300.raw", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(data_lines) + "\n")

    # 3. 构造充满干扰信息和乱码的 EXPLAIN ANALYZE 日志 (保留原有的环境复杂度)
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
DETAIL: Process 11055 waits for ShareLock on transaction; blocked by unknown.
HINT: Core dump generated for deep analysis.
\x00\x00\x00\x1F\x8B\x08\x00\x00\x00\x00\x00\x00\x03\x00 (Corrupted buffer tail)
    """
    
    with open("db_dumps/explain_analyze_garbage.log", "w", encoding="utf-8") as f:
        f.write(explain_content)
