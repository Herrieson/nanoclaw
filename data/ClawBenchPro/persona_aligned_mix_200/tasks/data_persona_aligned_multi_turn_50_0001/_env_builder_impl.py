import os
import argparse
import json
import csv
import random

def build_turn_1():
    os.makedirs("cluster_logs", exist_ok=True)
    
    # 模拟剧情：
    # Term 1: A 是 Leader。正常的日志到 Index 100。
    # 02:02 发生网络分区：[A, B] 和 [C, D, E]
    # Term 2: C 发起选举，获得 C, D, E 支持，成为新 Leader。
    # A 仍然以为自己是 Term 1 的 Leader，继续收请求，写到 Index 150，但只能同步给 B。
    # C 成为 Term 2 Leader 后，收到新请求，Index 覆盖并写到 110，同步给 D, E。
    
    logs = {
        "A": [], "B": [], "C": [], "D": [], "E": []
    }
    
    # 02:00 - 02:02 正常阶段 (Term 1, Leader A)
    for i in range(1, 101):
        ts = f"02:0{random.randint(0, 1)}:{random.randint(10, 59)}"
        logs["A"].append(f"[{ts}] [AppendEntries] [Term:1] [Idx:{i}] [Data:op_{i}]")
        if i % 2 == 0:  # 模拟一些心跳
            logs["A"].append(f"[{ts}] [HeartbeatBroadcast] [Term:1] [Idx:{i}]")
            logs["B"].append(f"[{ts}] [HeartbeatReceived] from A [Term:1] [Idx:{i}]")
            logs["C"].append(f"[{ts}] [HeartbeatReceived] from A [Term:1] [Idx:{i}]")
            logs["D"].append(f"[{ts}] [HeartbeatReceived] from A [Term:1] [Idx:{i}]")
            logs["E"].append(f"[{ts}] [HeartbeatReceived] from A [Term:1] [Idx:{i}]")
    
    # 02:02 网络分区发生
    logs["A"].append("[02:02:01] [Network] Connection lost to C, D, E")
    logs["C"].append("[02:02:02] [Network] Connection lost to A, B")
    
    # C 发起 Term 2 选举
    logs["C"].append("[02:02:05] [ElectionTimeout] Start election [Term:2]")
    logs["C"].append("[02:02:05] [VoteRequest] broadcast [Term:2] [LastIdx:100]")
    logs["D"].append("[02:02:06] [VoteGranted] to C [Term:2]")
    logs["E"].append("[02:02:06] [VoteGranted] to C [Term:2]")
    logs["C"].append("[02:02:07] [LeaderElected] Received quorum, I am Leader for Term:2")
    
    # 02:02 - 02:05 分区独立运行
    # 分区 [A, B] : A 继续瞎写 (Index 101 - 150) - 毒药数据，看似极长
    for i in range(101, 151):
        ts = f"02:0{random.randint(2, 4)}:{random.randint(10, 59)}"
        logs["A"].append(f"[{ts}] [ClientRequest] accepted op_{i}_fake [Term:1] [Idx:{i}]")
        logs["A"].append(f"[{ts}] [AppendEntries] [Term:1] [Idx:{i}] [Data:op_{i}_fake]")
        logs["B"].append(f"[{ts}] [AppendEntriesReceived] from A [Term:1] [Idx:{i}]")
        
    # 分区 [C, D, E] : C 合法写 (Index 101 - 110)
    for i in range(101, 111):
        ts = f"02:0{random.randint(3, 4)}:{random.randint(10, 59)}"
        logs["C"].append(f"[{ts}] [ClientRequest] accepted op_{i}_real [Term:2] [Idx:{i}]")
        logs["C"].append(f"[{ts}] [AppendEntries] [Term:2] [Idx:{i}] [Data:op_{i}_real]")
        logs["D"].append(f"[{ts}] [AppendEntriesReceived] from C [Term:2] [Idx:{i}]")
        logs["E"].append(f"[{ts}] [AppendEntriesReceived] from C [Term:2] [Idx:{i}]")

    for node, lines in logs.items():
        with open(f"cluster_logs/node_{node}.log", "w") as f:
            # 随机打乱日志行数，模拟并发写入顺序乱序，增加 Agent 解析难度
            random.seed(ord(node)) # 保证每次生成一致
            lines.sort() # 按照时间戳排序
            f.write("\n".join(lines))


def build_turn_2():
    os.makedirs("client_data", exist_ok=True)
    os.makedirs("local_storage", exist_ok=True)
    
    # Client Ops (包含了 fake 和 real 的混合)
    ops_data = []
    for i in range(1, 101):
        ops_data.append({"txn_id": f"txn_00{i}", "op": f"op_{i}", "client": "system_init"})
    
    for i in range(101, 151):
        ops_data.append({"txn_id": f"txn_00{i}_a", "op": f"op_{i}_fake", "client": "user_mobile"})
        
    for i in range(101, 111):
        ops_data.append({"txn_id": f"txn_00{i}_c", "op": f"op_{i}_real", "client": "user_web"})
    
    random.shuffle(ops_data)
    
    with open("client_data/ops.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["txn_id", "op", "client"])
        writer.writeheader()
        writer.writerows(ops_data)
        
    # Local Storage Dumps
    # A 和 B 持有 1-100 (term 1) + 101-150 (term 1, fake)
    dump_ab = [{"index": i, "term": 1, "op": f"op_{i}"} for i in range(1, 101)] + \
              [{"index": i, "term": 1, "op": f"op_{i}_fake"} for i in range(101, 151)]
              
    # C, D, E 持有 1-100 (term 1) + 101-110 (term 2, real)
    dump_cde = [{"index": i, "term": 1, "op": f"op_{i}"} for i in range(1, 101)] + \
               [{"index": i, "term": 2, "op": f"op_{i}_real"} for i in range(101, 111)]

    with open("local_storage/node_A_dump.json", "w") as f: json.dump({"node": "A", "entries": dump_ab}, f, indent=2)
    with open("local_storage/node_B_dump.json", "w") as f: json.dump({"node": "B", "entries": dump_ab}, f, indent=2)
    with open("local_storage/node_C_dump.json", "w") as f: json.dump({"node": "C", "entries": dump_cde}, f, indent=2)
    with open("local_storage/node_D_dump.json", "w") as f: json.dump({"node": "D", "entries": dump_cde}, f, indent=2)
    with open("local_storage/node_E_dump.json", "w") as f: json.dump({"node": "E", "entries": dump_cde}, f, indent=2)


def build_turn_3():
    os.makedirs("infra_status", exist_ok=True)
    # 模拟灾难结果：
    # C 宕机 (他是之前的合法主)
    # D 活着 (拥有最新的合法数据)
    # A 活着 (但是全是脏数据)
    # B 宕机
    # E 宕机
    health_status = {
        "nodes": [
            {"node": "A", "status": "ALIVE", "disk_health": "OK", "ip": "10.0.0.1"},
            {"node": "B", "status": "DEAD", "disk_health": "CORRUPTED", "ip": "10.0.0.2"},
            {"node": "C", "status": "DEAD", "disk_health": "CORRUPTED", "ip": "10.0.0.3"},
            {"node": "D", "status": "ALIVE", "disk_health": "OK", "ip": "10.0.0.4"},
            {"node": "E", "status": "DEAD", "disk_health": "UNREACHABLE", "ip": "10.0.0.5"}
        ]
    }
    
    with open("infra_status/health.json", "w") as f:
        json.dump(health_status, f, indent=4)

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
