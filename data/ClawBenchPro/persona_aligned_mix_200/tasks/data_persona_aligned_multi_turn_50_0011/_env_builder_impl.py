import os
import argparse
import json

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def build_turn_1():
    # 构造第一轮的环境
    pg_stat_content = """pid | datname | usename | application_name | state | wait_event_type | wait_event | blocking_pids | query
------+---------+---------+------------------+---------------------+-----------------+------------+---------------+------------------------------------------------------
 1001 | prod_db | appuser | inventory_worker | idle in transaction |                 |            | {}            | UPDATE inventory SET stock = stock - 1 WHERE item_id = 42;
 1002 | prod_db | appuser | order_service    | active              | Lock            | tuple      | {1001}        | SELECT * FROM inventory WHERE item_id = 42 FOR UPDATE;
 1003 | prod_db | appuser | order_service    | active              | Lock            | tuple      | {1001,1002}   | SELECT * FROM inventory WHERE item_id = 42 FOR UPDATE;
 1004 | prod_db | appuser | payment_gateway  | active              | Lock            | tuple      | {1001,1002}   | SELECT * FROM inventory WHERE item_id = 42 FOR UPDATE;
 1005 | prod_db | appuser | order_service    | active              | Lock            | tuple      | {1001,1002}   | SELECT * FROM inventory WHERE item_id = 42 FOR UPDATE;
 1006 | prod_db | appuser | reporting_tool   | active              |                 |            | {}            | SELECT count(*) FROM users;
 1007 | prod_db | appuser | order_service    | active              | Lock            | tuple      | {1001,1002}   | SELECT * FROM inventory WHERE item_id = 42 FOR UPDATE;
"""
    create_file("snapshots/pg_stat_activity_10_00.txt", pg_stat_content)

    slow_query_content = """2023-10-25 10:00:15 UTC [1001] LOG:  duration: 1500.452 ms  plan:
Query Text: UPDATE inventory SET stock = stock - 1 WHERE item_id = 42;
Update on inventory  (cost=0.00..8.45 rows=1 width=14) (actual time=1500.450..1500.451 rows=0 loops=1)
  ->  Index Scan using idx_item on inventory  (cost=0.00..8.45 rows=1 width=14) (actual time=0.015..0.017 rows=1 loops=1)
        Index Cond: (item_id = 42)

2023-10-25 10:00:20 UTC [1006] LOG:  duration: 5000.112 ms  plan:
Query Text: SELECT count(*) FROM users;
Aggregate  (cost=15000.00..15000.01 rows=1 width=8)
  ->  Seq Scan on users  (cost=0.00..10000.00 rows=500000 width=0)
"""
    create_file("query_logs/slow_queries_10_00.log", slow_query_content)
    os.makedirs("reports", exist_ok=True)

def build_turn_2():
    # 构造第二轮的环境，继承或注入新数据
    pg_stat_content = """pid | datname | usename | application_name | state | wait_event_type | wait_event | blocking_pids | query
------+---------+---------+------------------+---------------------+-----------------+------------+---------------+------------------------------------------------------
 2001 | prod_db | appuser | inventory_worker | idle in transaction |                 |            | {}            | UPDATE inventory SET stock = stock - 1 WHERE item_id = 99;
 2002 | prod_db | appuser | order_service    | active              | Lock            | tuple      | {2001}        | SELECT * FROM inventory WHERE item_id = 99 FOR UPDATE;
 3001 | prod_db | rptuser | legacy_reporter  | active              |                 |            | {}            | SELECT pg_sleep(3600), * FROM monthly_reports;
 3002 | prod_db | appuser | dashboard_ui     | active              | Lock            | relation   | {3001}        | SELECT count(*) FROM monthly_reports;
 4001 | prod_db | appuser | marketing_sync   | active              |                 |            | {}            | ALTER TABLE users ADD COLUMN ltv numeric;
 4002 | prod_db | appuser | login_service    | active              | Lock            | relation   | {4001}        | SELECT * FROM users WHERE username = 'admin';
 4003 | prod_db | appuser | login_service    | active              | Lock            | relation   | {4001}        | SELECT * FROM users WHERE username = 'test';
 4004 | prod_db | appuser | login_service    | active              | Lock            | relation   | {4001}        | SELECT * FROM users WHERE username = 'guest';
"""
    create_file("snapshots/pg_stat_activity_14_00.txt", pg_stat_content)

    whitelist_content = {
        "exemptions": [
            {
                "application_name": "legacy_reporter",
                "target_tables": ["monthly_reports"],
                "justification": "End of month heavy aggregation, exclusive relation lock expected."
            }
        ]
    }
    create_file("config/whitelist.json", json.dumps(whitelist_content, indent=4))
    os.makedirs("reports", exist_ok=True)

def build_turn_3():
    # 构造第三轮的环境，SQL补丁审查
    pr_101 = """-- PR 101: Optimize inventory updates
-- Adding a composite index to speed up the update scan
CREATE INDEX idx_inventory_item_stock ON inventory(item_id, stock);
"""
    create_file("patches/pr_101.sql", pr_101)

    pr_102 = """-- PR 102: Fix connection leak in inventory worker
-- The application was opening a transaction, running an UPDATE, and then waiting for an external API call before committing.
-- This patch moves the external API call outside the database transaction.
BEGIN;
UPDATE inventory SET stock = stock - 1 WHERE item_id = $1;
COMMIT;
-- API call happens here now, DB connection is already released
"""
    create_file("patches/pr_102.sql", pr_102)

    pr_103 = """-- PR 103: Resolve all blocking issues
-- Kill the legacy reporter queries that block the dashboard
DROP TABLE monthly_reports CASCADE;
CREATE VIEW monthly_reports AS SELECT * FROM users;

-- Also fix the inventory
BEGIN;
UPDATE inventory SET stock = stock - 1 WHERE item_id = $1;
COMMIT;
"""
    create_file("patches/pr_103.sql", pr_103)
    os.makedirs("reports", exist_ok=True)


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
