import os
import random
import json

def chunk_string(s, length=64):
    """将字符串切分为指定长度的行，模拟真实的 buffer 换行输出"""
    return '\n'.join(s[i:i+length] for i in range(0, len(s), length))

def generate_hex(bytes_len):
    """生成指定字节长度的随机十六进制字符串（每个字节占2个字符）"""
    return ''.join(random.choices("0123456789ABCDEF", k=bytes_len * 2))

def build_env():
    # 固定种子以保证沙箱的可重复性
    random.seed(730073)
    
    os.makedirs("optimizations", exist_ok=True)
    base_log_dir = "cluster_logs"
    os.makedirs(base_log_dir, exist_ok=True)

    # 预定义配置
    nodes_count = 15
    sessions_per_node = 20
    
    phases = ["SETUP", "GARBLING", "EVALUATE", "OT_EXTENSION"]
    versions = ["v2.1", "v2.5-beta", "v3.0-RC", "legacy_v1"]
    
    # 我们需要找出积累在有效条件下的前三大门
    # 有效条件: phase == "EVALUATE" and version == "v3.0-RC"
    target_gates = ["GATE_8F4A", "GATE_2B99", "GATE_7C1D"]
    # 分配目标载荷（纯字符数）： 8F4A: ~150000, 2B99: ~120000, 7C1D: ~90000
    
    decoy_gate = "GATE_FFFF" # 将在 GARBLING 阶段注入，载荷极大，用于诱捕没有过滤元数据的 Agent
    
    normal_gate_pool = [f"GATE_{i:04X}" for i in range(100, 300)]

    valid_sessions = []
    all_sessions = []

    # 1. 预生成会话元数据
    for n in range(nodes_count):
        for s in range(sessions_per_node):
            all_sessions.append((n, s))

    # 强制让约 50 个 Session 成为 valid session
    valid_indices = set(random.sample(range(len(all_sessions)), 50))

    for i, (n, s) in enumerate(all_sessions):
        node_dir = os.path.join(base_log_dir, f"node_{n:02d}")
        session_dir = os.path.join(node_dir, f"session_{s:03d}")
        os.makedirs(session_dir, exist_ok=True)

        is_valid = i in valid_indices
        if is_valid:
            phase = "EVALUATE"
            version = "v3.0-RC"
            valid_sessions.append(session_dir)
        else:
            phase = random.choice([p for p in phases if p != "EVALUATE"] + ["EVALUATE"])
            version = random.choice([v for v in versions if v != "v3.0-RC"] + ["v3.0-RC"])
            # 如果随机到了有效条件，强制改掉，确保我们的控制组纯净
            if phase == "EVALUATE" and version == "v3.0-RC":
                phase = "GARBLING"

        # 写入元数据
        meta_data = {
            "session_id": f"S_{n:02d}_{s:03d}",
            "node": f"node_{n:02d}",
            "phase": phase,
            "protocol_version": version,
            "curve": "secp256k1",
            "parties": 3
        }
        with open(os.path.join(session_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=4)

        # 写入日志数据
        with open(os.path.join(session_dir, "trace.log"), "w", encoding="utf-8") as f:
            f.write(f"=== MPC CORE ENGINE DIAGNOSTIC LOG ===\n")
            f.write(f"SESSION: {meta_data['session_id']} | PHASE: {phase}\n\n")

            gates_to_write = []
            
            # 正常背景噪音门（数量和载荷随机）
            for _ in range(random.randint(20, 50)):
                gid = random.choice(normal_gate_pool)
                gtype = random.choice(["XOR", "AND", "INV", "XNOR"])
                payload = generate_hex(random.randint(10, 50)) # 20~100 chars
                gates_to_write.append((gid, gtype, payload))

            # 根据会话有效性注入特定门
            if is_valid:
                # 给有效会话均匀注入目标 Gate
                # 让 target_gates 累积起来最大
                gates_to_write.append((target_gates[0], "AND", generate_hex(1500))) # 3000 chars * 50 sessions = 150000
                gates_to_write.append((target_gates[1], "AND", generate_hex(1200))) # 2400 chars * 50 sessions = 120000
                gates_to_write.append((target_gates[2], "AND", generate_hex(900)))  # 1800 chars * 50 sessions =  90000
            else:
                if phase == "GARBLING":
                    # 致命诱饵：在错误的阶段生成一个极大的 payload，约 80000 字符
                    if random.random() < 0.2:
                        gates_to_write.append((decoy_gate, "AND", generate_hex(40000)))

            # 打乱顺序
            random.shuffle(gates_to_write)

            for gid, gtype, payload in gates_to_write:
                f.write(f"--- [OP_TRACE] {gid} [{gtype}] ---\n")
                if random.random() < 0.3:
                    f.write(f"state_check: OK (wire_entropy={random.uniform(0.9, 1.0):.4f})\n")
                if random.random() < 0.15:
                    f.write(f"warn: minor sync delay at {gid}, auto-recovered.\n")
                    
                f.write("== WIRE_EXCHANGE_BUFFER ==\n")
                # 注入大量换行和空白作为干扰（Agent必须过滤它们）
                formatted_payload = chunk_string(payload, random.choice([32, 64, 128]))
                f.write(formatted_payload + "\n")
                f.write("== END_BUFFER ==\n\n")

if __name__ == "__main__":
    build_env()
