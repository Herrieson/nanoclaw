import os
import json
import random
import string
import uuid

def build_env():
    # 初始化环境目录，当前工作目录已经设定为 assets/data_persona_aligned_hard_50_0046/
    os.makedirs("snapshots/lock_dumps", exist_ok=True)
    os.makedirs("emergency_ops", exist_ok=True)
    for i in range(100):
        os.makedirs(f"snapshots/traces/{i:02d}", exist_ok=True)
        
    random.seed(42)
    
    # 构建隐藏的真实链路
    # 真实链条: 3041 -> 4092 -> 5103 -> 8821(真正的源头, active, wait NULL)
    true_chain = [3041, 4092, 5103, 8821]
    target_xid = "0x8F4B2A"
    
    edges = []
    # 注入真实阻塞链路
    edges.append(f"TIMESTAMP: 2023-10-27T03:15:01 || <PID:{true_chain[0]}> || STATE:active || WAIT_ON_PID:{true_chain[1]} || QUERY: UPDATE orders SET status = 'PAID' WHERE id = 12093;")
    edges.append(f"TIMESTAMP: 2023-10-27T03:15:02 || <PID:{true_chain[1]}> || STATE:active || WAIT_ON_PID:{true_chain[2]} || QUERY: UPDATE inventory SET stock = stock - 1 WHERE item_id = 44;")
    edges.append(f"TIMESTAMP: 2023-10-27T03:15:03 || <PID:{true_chain[2]}> || STATE:active || WAIT_ON_PID:{true_chain[3]} || QUERY: DELETE FROM order_locks WHERE lock_id = 991;")
    edges.append(f"TIMESTAMP: 2023-10-27T03:15:04 || <PID:{true_chain[3]}> || STATE:active || WAIT_ON_PID:NULL || QUERY: VACUUM FULL user_profiles;")
    
    # 注入大量的干扰噪音（伪造阻塞与非活动源头）
    for _ in range(350):
        # 注意：干扰 PID 使用 5 位数，确保不会与 4位数的 8821 意外冲突
        p1 = random.randint(10000, 99999)
        p2 = random.randint(10000, 99999)
        state = random.choice(['idle', 'active', 'idle_in_transaction'])
        edges.append(f"TIMESTAMP: 2023-10-27T03:{random.randint(10,59):02d}:{random.randint(10,59):02d} || <PID:{p1}> || STATE:{state} || WAIT_ON_PID:{p2} || QUERY: SELECT pg_sleep(1);")
        
        # 制造“虚假源头”：等待 NULL，但状态是 idle，这是诱饵！
        if random.random() < 0.15:
            edges.append(f"TIMESTAMP: 2023-10-27T03:{random.randint(10,59):02d}:{random.randint(10,59):02d} || <PID:{p2}> || STATE:idle || WAIT_ON_PID:NULL || QUERY: COMMIT;")
            
    # 打乱所有有向图边
    random.shuffle(edges)
    
    # 将日志切片分发到几十个独立的文件中（信息碎片化）
    chunk_size = 8
    for i in range(50):
        with open(f"snapshots/lock_dumps/shard_dump_{i:03d}.log", "w") as f:
            lines_to_write = []
            # 添加纯粹的废土风格无意义报错日志
            for _ in range(15):
                lines_to_write.append(f"~#~#~ MEM DUMP CORRUPTION DETECTED AT 0x{random.randint(100000,999999):X} " + "".join(random.choices(string.ascii_letters, k=25)))
            
            # 填入边片段
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(edges))
            lines_to_write.extend(edges[start_idx:end_idx])
            
            random.shuffle(lines_to_write)
            f.write("\n".join(lines_to_write))

    # --- 阶段 2: 生成成百上千个 trace 文件 ---
    def create_nested_noise(depth, core_payload):
        if depth == 0:
            return core_payload
        return {
            f"Node_{random.randint(1, 100)}": create_nested_noise(depth - 1, core_payload),
            "ExtraMetadata": "N/A",
            "GarbageDump": "".join(random.choices(string.ascii_letters, k=30))
        }

    # 生成 1000 个分散的 JSON 文件以形成规模压制
    for j in range(1000):
        pid = random.randint(10000, 99999)
        is_target = False
        
        # 将真相藏在第 666 次循环
        if j == 666:
            pid = true_chain[3] # 8821
            is_target = True
            
        shard_dir = f"snapshots/traces/{pid % 100:02d}"
        trace_id = f"trace_evt_{uuid.uuid4()}"
        
        if is_target:
            # 真理结构：包含内部被 stringify 转义的 JSON
            internal_payload = {
                "layer1_diagnostics": {
                    "layer2_plan": {
                        "execution_details": {
                            "XID_HEX": target_xid,
                            "lock_type": "AccessExclusiveLock"
                        }
                    }
                }
            }
            core_content = {
                "process_metadata": {"process_id": pid},
                "status": "CRITICAL_OOM",
                "serialized_execution_plan": json.dumps(internal_payload) # 再次字符串化
            }
        else:
            internal_payload = {
                "layer1_diagnostics": {
                    "layer2_plan": {
                        "execution_details": {
                            "XID_HEX": f"0x{random.randint(100000, 999999):X}",
                            "lock_type": random.choice(["AccessShareLock", "RowShareLock"])
                        }
                    }
                }
            }
            core_content = {
                "process_metadata": {"process_id": pid},
                "status": "NORMAL",
                "serialized_execution_plan": json.dumps(internal_payload)
            }
            
        # 将核心内容包裹进多层噪声 JSON
        final_json = create_nested_noise(4, core_content)
        
        with open(f"{shard_dir}/{trace_id}.json", "w") as f:
            json.dump(final_json, f, separators=(',', ':'))

if __name__ == "__main__":
    build_env()
