import os
import argparse
import csv
import json

def build_turn_1():
    # 模拟 Turn 1: 构建锁等待图的初始状态
    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("explain_logs", exist_ok=True)

    # 活动快照 (Root blockers: 1001, 5005)
    # 陷阱：2002 看起来是 blocker，但它被 1001 阻塞。1001 是真正的 root。
    # 陷阱：5005 是 root，但 duration 只有 2 秒，不符合 turn 1 的 > 5 秒阈值。
    # 所以 Turn 1 唯一真正的严重根源阻塞者是 1001。
    activity_data = [
        {"pid": "1001", "state": "active", "duration_sec": "12", "blocking_pids": "[]", "query": "SELECT * FROM orders WHERE status = 'PENDING';"},
        {"pid": "1002", "state": "active", "duration_sec": "10", "blocking_pids": "[1001]", "query": "UPDATE orders SET status = 'PROCESSING' WHERE order_id = 999;"},
        {"pid": "1003", "state": "active", "duration_sec": "9", "blocking_pids": "[1001]", "query": "UPDATE orders SET status = 'PROCESSING' WHERE order_id = 998;"},
        {"pid": "1004", "state": "active", "duration_sec": "8", "blocking_pids": "[1002]", "query": "SELECT * FROM order_items WHERE order_id = 999;"},
        
        {"pid": "2001", "state": "active", "duration_sec": "15", "blocking_pids": "[2002]", "query": "DELETE FROM sessions WHERE expired = true;"},
        {"pid": "2002", "state": "active", "duration_sec": "14", "blocking_pids": "[1001]", "query": "UPDATE orders SET updated_at = now();"},
        
        {"pid": "5005", "state": "active", "duration_sec": "2", "blocking_pids": "[]", "query": "SELECT * FROM inventory WHERE stock < 10;"},
        {"pid": "5006", "state": "active", "duration_sec": "1", "blocking_pids": "[5005]", "query": "UPDATE inventory SET stock = stock - 1 WHERE item_id = 1;"}
    ]

    with open("snapshots/activity_10_00.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["pid", "state", "duration_sec", "blocking_pids", "query"])
        writer.writeheader()
        writer.writerows(activity_data)

    explain_logs = """
Query: SELECT * FROM orders WHERE status = 'PENDING';
Plan:
->  Seq Scan on orders  (cost=0.00..15432.00 rows=4320 width=128) (actual time=0.012..43.210 rows=4000 loops=1)
      Filter: ((status)::text = 'PENDING'::text)
      Rows Removed by Filter: 980000

Query: SELECT * FROM inventory WHERE stock < 10;
Plan:
->  Seq Scan on inventory  (cost=0.00..8321.00 rows=120 width=64)
      Filter: (stock < 10)
"""
    with open("explain_logs/query_plans.txt", "w") as f:
        f.write(explain_logs)


def build_turn_2():
    # 模拟 Turn 2: 新增 VIP 逻辑与应用日志
    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("app_logs", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    os.makedirs("explain_logs", exist_ok=True)

    # 陷阱：Agent必须从自己的记录里恢复 "duration > 5" 这个条件
    # 新的 Root Blockers:
    # 8080: duration=8 (严重), root. 用户ID: U_999 (非VIP) -> 应当 Kill
    # 9090: duration=15 (严重), root. 用户ID: U_001 (VIP) -> 应当 Throttle
    # 7070: duration=3 (不严重), root.
    activity_11_00 = [
        {"pid": "8080", "state": "active", "duration_sec": "8", "blocking_pids": "[]", "query": "SELECT * FROM payment_logs WHERE gateway = 'STRIPE';"},
        {"pid": "8081", "state": "active", "duration_sec": "7", "blocking_pids": "[8080]", "query": "UPDATE payment_logs SET synced = true;"},
        
        {"pid": "9090", "state": "active", "duration_sec": "15", "blocking_pids": "[]", "query": "SELECT * FROM user_rewards WHERE points > 1000;"},
        {"pid": "9091", "state": "active", "duration_sec": "10", "blocking_pids": "[9090]", "query": "INSERT INTO user_rewards (user_id) VALUES (U_001);"},

        {"pid": "7070", "state": "active", "duration_sec": "3", "blocking_pids": "[]", "query": "SELECT * FROM audit_trail;"}
    ]
    with open("snapshots/activity_11_00.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["pid", "state", "duration_sec", "blocking_pids", "query"])
        writer.writeheader()
        writer.writerows(activity_11_00)

    # 应用映射日志
    app_logs = """
[INFO] PID:8080 Transaction started by user_id: U_999
[INFO] PID:8081 Transaction started by user_id: U_999
[INFO] PID:9090 Transaction started by user_id: U_001
[INFO] PID:7070 Transaction started by system_cron
"""
    with open("app_logs/tx_params.log", "w") as f:
        f.write(app_logs.strip())

    # VIP 名单
    with open("reference/vip_list.json", "w") as f:
        json.dump({"vips": ["U_001", "U_002", "U_008"]}, f)

    # 提前备好 Turn 3 会用到的 Explain plans (放在11_00的log里)
    explain_logs_11 = """
Query: SELECT * FROM payment_logs WHERE gateway = 'STRIPE';
Plan:
->  Seq Scan on payment_logs  (cost=0.00..29321.00 rows=50000 width=256)
      Filter: ((gateway)::text = 'STRIPE'::text)

Query: SELECT * FROM user_rewards WHERE points > 1000;
Plan:
->  Seq Scan on user_rewards  (cost=0.00..12000.00 rows=500 width=64)
      Filter: (points > 1000)
"""
    with open("explain_logs/query_plans_11_00.txt", "w") as f:
        f.write(explain_logs_11)

def build_turn_3():
    # 模拟 Turn 3: 给出 Schema，要求写 SQL patch
    # 这里的挑战在于Agent必须只针对 turn 2 中 kill 的非 VIP(payment_logs, gateway) 生成索引，而不要给 VIP(user_rewards) 建索引。
    os.makedirs("schema", exist_ok=True)
    schema_sql = """
CREATE TABLE payment_logs (
    log_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    gateway VARCHAR(50),
    amount DECIMAL,
    synced BOOLEAN,
    created_at TIMESTAMP
);

CREATE TABLE user_rewards (
    reward_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    points INT,
    issued_at TIMESTAMP
);
"""
    with open("schema/tables.sql", "w") as f:
        f.write(schema_sql.strip())


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
