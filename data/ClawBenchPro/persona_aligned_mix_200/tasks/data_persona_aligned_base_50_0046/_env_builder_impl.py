import os
import json
import random
import string

def build_env():
    # 建立目录结构 (此时工作目录已经是 assets/data_persona_aligned_base_50_0046/)
    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("emergency_ops", exist_ok=True)
    
    # 使用固定随机种子以保证评测环境的确定性
    random.seed(42)
    
    # 构造一条隐蔽的阻塞链
    # 3041 (等待) -> 4092 (等待) -> 5103 (等待) -> 8821 (源头阻塞者)
    chain = [3041, 4092, 5103, 8821]
    target_xid = "0x8F4B2A"
    
    # 1. 生成充满脏数据和干扰项的 pg_stat_activity 快照
    lines = []
    noise_pids = [1024, 2048, 3055, 4088, 5099, 6100, 7122]
    
    # 注入干扰日志
    for pid in noise_pids:
        lines.append(f"[{random.randint(100000, 999999)}] <{pid}>||state=idle||wait=NULL||query=SELECT pg_sleep(1);")
        lines.append(f"0x00007f{random.randint(100000, 999999)} kernel trace interrupt - buffer ring corrupted")
        lines.append(f"~#~#~ MEM DUMP {random.choice(string.ascii_letters)*10}")
        
    # 注入真实的阻塞链
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:01 || <PID:{chain[0]}> || STATE:active || WAIT_ON_PID:{chain[1]} || QUERY: UPDATE orders SET status = 'PAID' WHERE id = 12093;")
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:02 || <PID:{chain[1]}> || STATE:active || WAIT_ON_PID:{chain[2]} || QUERY: UPDATE inventory SET stock = stock - 1 WHERE item_id = 44;")
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:03 || <PID:{chain[2]}> || STATE:active || WAIT_ON_PID:{chain[3]} || QUERY: DELETE FROM order_locks WHERE lock_id = 991;")
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:04 || <PID:{chain[3]}> || STATE:active || WAIT_ON_PID:NULL || QUERY: VACUUM FULL user_profiles;")
    
    random.shuffle(lines)
    
    with open("snapshots/pg_stat_activity_dump.log", "w") as f:
        f.write("=== PG_STAT_ACTIVITY EMERGENCY DUMP ===\n")
        f.write("WARNING: FORMAT CORRUPTED - PARTIAL HEX DUMPS DETECTED\n")
        f.write("------------------------------------------------------\n\n")
        f.write("\n".join(lines))
        f.write("\n\nEOF\n")

    # 2. 生成嵌套极深的 EXPLAIN ANALYZE JSON 日志
    def create_nested_noise(depth):
        if depth == 0:
            return "".join(random.choices(string.ascii_letters + string.digits, k=12))
        return {
            f"TraceNode_{random.randint(1, 50)}": create_nested_noise(depth - 1),
            f"ExecutionInfo_{random.randint(1, 50)}": [create_nested_noise(depth - 1)]
        }

    root_data = {
        "DiagnosticID": "DIAG-P0-991-CRITICAL",
        "Timestamp": "2023-10-27T03:15:05Z",
        "TracedProcesses": []
    }

    # 构造目标进程的深层嵌套结构
    target_process = {
        "ProcessMetadata": {
            "OS_PID": chain[3],
            "Worker": "Background Worker 01",
            "ExecutionPlan": {
                "Plan": {
                    "NodeType": "Vacuum",
                    "RelationName": "user_profiles",
                    "TransactionState": {
                        "Status": "IN_PROGRESS",
                        "IsolationLevel": "SERIALIZABLE",
                        "LocksHeld": [{"LockType": "AccessExclusiveLock", "Granted": True}],
                        "XID_HEX": target_xid
                    }
                }
            }
        }
    }

    # 将目标数据包裹在极度深层的随机键值对中
    deep_target = create_nested_noise(4)
    deep_target[f"TraceNode_{random.randint(1,50)}"] = {"Injected_Trace_Payload": target_process}

    # 注入干扰进程
    for pid in noise_pids + chain[:-1]:
        root_data["TracedProcesses"].append({
            "ProcessMetadata": {
                "OS_PID": pid,
                "Worker": f"Client Backend {random.randint(10, 99)}",
                "ExecutionPlan": create_nested_noise(2)
            }
        })

    # 将隐藏了答案的深层节点加入进程列表
    root_data["TracedProcesses"].append({"DeeplyNestedTraceAnomaly": deep_target})
    random.shuffle(root_data["TracedProcesses"])

    with open("snapshots/explain_analyze_traces.json", "w") as f:
        json.dump(root_data, f, indent=2)

if __name__ == "__main__":
    build_env()
