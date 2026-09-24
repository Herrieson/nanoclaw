import os
import argparse
import json
import csv
from datetime import datetime, timedelta

def build_turn_1():
    os.makedirs("db_snapshots", exist_ok=True)
    os.makedirs("conf", exist_ok=True)

    # 慢查询阈值配置
    thresholds = {
        "ecommerce_db": 500,  # 毫秒
        "user_center_db": 200,
        "log_db": 2000
    }
    with open("conf/slow_query_thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=4)

    # 伪造时间基准
    base_time = datetime.now()
    
    # 构造 pg_stat_activity
    # PID 101: 阻塞根节点，持锁不放，idle in transaction
    # PID 102: 被 101 阻塞
    # PID 103: 被 102 阻塞
    # PID 201: 极慢的查询 (ecommerce_db, 耗时800ms > 500ms)
    # PID 202: 正常的查询 (ecommerce_db, 耗时100ms)
    # PID 999: 系统进程，无害
    activity_data = [
        {"pid": 101, "datname": "ecommerce_db", "usename": "dev_reckless", "state": "idle in transaction", "query": "UPDATE orders SET status='PROCESSING' WHERE id=5;", "query_start": (base_time - timedelta(minutes=5)).isoformat()},
        {"pid": 102, "datname": "ecommerce_db", "usename": "dev_junior", "state": "active", "query": "UPDATE orders SET status='DONE' WHERE id=5;", "query_start": (base_time - timedelta(seconds=30)).isoformat()},
        {"pid": 103, "datname": "ecommerce_db", "usename": "dev_reckless", "state": "active", "query": "SELECT * FROM orders WHERE id=5 FOR UPDATE;", "query_start": (base_time - timedelta(seconds=20)).isoformat()},
        {"pid": 201, "datname": "user_center_db", "usename": "dev_intern", "state": "active", "query": "SELECT * FROM users WHERE age > 18;", "query_start": (base_time - timedelta(milliseconds=850)).isoformat()},
        {"pid": 202, "datname": "user_center_db", "usename": "dev_senior", "state": "active", "query": "SELECT * FROM users WHERE id = 1;", "query_start": (base_time - timedelta(milliseconds=10)).isoformat()},
        {"pid": 999, "datname": "log_db", "usename": "system", "state": "idle", "query": "INSERT INTO logs...", "query_start": (base_time - timedelta(hours=1)).isoformat()}
    ]
    with open("db_snapshots/pg_stat_activity_0300.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=activity_data[0].keys())
        writer.writeheader()
        writer.writerows(activity_data)

    # 构造 pg_locks
    # 模拟 101 持有 relation 1000 的锁
    # 102 请求 relation 1000 的锁被拒，同时持有 relation 2000 的锁
    # 103 请求 relation 2000 的锁被拒
    locks_data = [
        {"locktype": "relation", "database": "ecommerce_db", "relation": "1000", "pid": 101, "mode": "ExclusiveLock", "granted": "true"},
        {"locktype": "relation", "database": "ecommerce_db", "relation": "1000", "pid": 102, "mode": "ExclusiveLock", "granted": "false"},
        {"locktype": "relation", "database": "ecommerce_db", "relation": "2000", "pid": 102, "mode": "ExclusiveLock", "granted": "true"},
        {"locktype": "relation", "database": "ecommerce_db", "relation": "2000", "pid": 103, "mode": "ExclusiveLock", "granted": "false"},
        {"locktype": "relation", "database": "user_center_db", "relation": "3000", "pid": 201, "mode": "AccessShareLock", "granted": "true"},
        {"locktype": "relation", "database": "user_center_db", "relation": "3000", "pid": 202, "mode": "AccessShareLock", "granted": "true"},
        # 加一个死锁孤岛作为陷阱，这两个没有导致大面积阻塞且自身都在等，无根
        {"locktype": "relation", "database": "log_db", "relation": "4000", "pid": 401, "mode": "ExclusiveLock", "granted": "false"},
        {"locktype": "relation", "database": "log_db", "relation": "5000", "pid": 402, "mode": "ExclusiveLock", "granted": "false"}
    ]
    with open("db_snapshots/pg_locks_0300.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=locks_data[0].keys())
        writer.writeheader()
        writer.writerows(locks_data)

def build_turn_2():
    # 上下文关联：高危执行人是 dev_reckless (根PID 101) 和 dev_intern (慢查询PID 201)。
    # dev_junior 是无辜受害者，dev_senior 是正常人。
    os.makedirs("explain_logs", exist_ok=True)
    
    # 日志1: dev_reckless 的罪证。Seq Scan，过滤率 99%
    log1 = """EXPLAIN ANALYZE SELECT * FROM orders_history WHERE status = 'FAILED' AND retry_count > 5;
Seq Scan on orders_history  (cost=0.00..34521.00 rows=150 width=120) (actual time=0.021..450.120 rows=10 loops=1)
  Filter: ((status = 'FAILED'::text) AND (retry_count > 5))
  Rows Removed by Filter: 990
Planning Time: 0.120 ms
Execution Time: 450.500 ms"""
    with open("explain_logs/query_dev_reckless_1.txt", "w") as f: f.write(log1)
    
    # 日志2: dev_intern 的罪证。Seq Scan，过滤率 95%
    log2 = """EXPLAIN ANALYZE SELECT * FROM user_behaviors WHERE action_type = 'CLICK' AND platform = 'IOS';
Seq Scan on user_behaviors  (cost=0.00..56000.00 rows=500 width=80) (actual time=0.040..800.000 rows=50 loops=1)
  Filter: ((action_type = 'CLICK'::text) AND (platform = 'IOS'::text))
  Rows Removed by Filter: 950
Planning Time: 0.200 ms
Execution Time: 800.300 ms"""
    with open("explain_logs/query_dev_intern_1.txt", "w") as f: f.write(log2)

    # 日志3: dev_senior (清白人)。虽然是 Seq Scan 且过滤率极高，但不能抓他！(陷阱)
    log3 = """EXPLAIN ANALYZE SELECT * FROM system_configs WHERE key = 'MAINTENANCE_MODE';
Seq Scan on system_configs  (cost=0.00..10.00 rows=1 width=50) (actual time=0.010..0.050 rows=1 loops=1)
  Filter: (key = 'MAINTENANCE_MODE'::text)
  Rows Removed by Filter: 99
Planning Time: 0.050 ms
Execution Time: 0.060 ms"""
    with open("explain_logs/query_dev_senior_1.txt", "w") as f: f.write(log3)

    # 日志4: dev_reckless (高危人员)。但使用了 Index Scan，过滤率低，不符合条件 (陷阱)
    log4 = """EXPLAIN ANALYZE SELECT * FROM orders_history WHERE id = 999;
Index Scan using pk_orders_history on orders_history  (cost=0.42..8.44 rows=1 width=120) (actual time=0.015..0.016 rows=1 loops=1)
  Index Cond: (id = 999)
Planning Time: 0.100 ms
Execution Time: 0.030 ms"""
    with open("explain_logs/query_dev_reckless_2.txt", "w") as f: f.write(log4)

def build_turn_3():
    # 上下文关联：
    # 高危执行人：dev_reckless, dev_intern
    # 重灾区表名：orders_history, user_behaviors
    os.makedirs("maintenance", exist_ok=True)
    
    # 模拟 YAML 配置草案
    draft_yaml = """# 数据库连接池按用户限制草案
pools:
  dev_reckless:
    max_connections: 50
  dev_intern:
    max_connections: 20
  dev_junior:
    max_connections: 30
  dev_senior:
    max_connections: 100
  system:
    max_connections: 500
"""
    with open("maintenance/pool_config_draft.yaml", "w") as f:
        f.write(draft_yaml)
        
    # 模拟 CSV 索引提议
    proposals = [
        {"table_name": "orders_history", "column": "status, retry_count", "index_type": "BTREE", "reason": "High Seq Scan"},
        {"table_name": "user_behaviors", "column": "action_type, platform", "index_type": "BTREE", "reason": "High filtering"},
        {"table_name": "system_configs", "column": "key", "index_type": "HASH", "reason": "Fast lookup"}, # 陷阱，不是重灾区
        {"table_name": "orders", "column": "created_at", "index_type": "BRIN", "reason": "Time series"}, # 陷阱，不是重灾区
        {"table_name": "users", "column": "age", "index_type": "BTREE", "reason": "Slow query fix"} # 陷阱，虽有慢查询但turn2中并未爆出全表扫描罪证
    ]
    with open("maintenance/index_proposals.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=proposals[0].keys())
        writer.writeheader()
        writer.writerows(proposals)

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
