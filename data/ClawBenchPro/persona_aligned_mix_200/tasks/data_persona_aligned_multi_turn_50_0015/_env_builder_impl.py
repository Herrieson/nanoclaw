import os
import argparse
import json
import csv

def build_turn_1():
    # 创建目录
    os.makedirs("node_logs", exist_ok=True)
    os.makedirs("circuit_configs", exist_ok=True)
    
    # 构造 circuit configs
    gates = {
        "gate_1001": {"gate_type": "AND_GATE", "obfuscation_rounds": 128, "memory_alloc": "high"},
        "gate_1002": {"gate_type": "XOR_GATE", "obfuscation_rounds": 64, "memory_alloc": "low"},
        "gate_1003": {"gate_type": "INV_GATE", "obfuscation_rounds": 32, "memory_alloc": "low"},
        "gate_1004": {"gate_type": "AND_GATE", "obfuscation_rounds": 256, "memory_alloc": "critical"}
    }
    
    for gid, config in gates.items():
        with open(f"circuit_configs/{gid}.json", "w") as f:
            json.dump(config, f, indent=4)
            
    # 构造 node logs (干扰项与目标)
    # 规则：payload > 85000 且 包含 0000/ffff 前缀
    logs = [
        # NODE_A: 正常
        "[2023-10-24 01:00:01] NODE_A | Payload: 45000 bytes | BigInt_Hex: 1a2b3c4d5e6f | gate_id: gate_1002",
        "[2023-10-24 01:00:05] NODE_A | Payload: 46000 bytes | BigInt_Hex: a1b2c3d4e5f6 | gate_id: gate_1002",
        
        # NODE_B: 异常 (符合条件, 前缀0000) -> gate_1001 (AND)
        "[2023-10-24 01:01:12] NODE_B | Payload: 86500 bytes | BigInt_Hex: 0000a9b8c7d6 | gate_id: gate_1001",
        
        # NODE_C: 陷阱 (流量极大，但无低熵前缀) -> 不要杀它
        "[2023-10-24 01:02:44] NODE_C | Payload: 150000 bytes | BigInt_Hex: 8f7e6d5c4b3a | gate_id: gate_1004",
        
        # NODE_D: 异常 (符合条件, 前缀FFFF) -> gate_1003 (INV)
        "[2023-10-24 01:03:09] NODE_D | Payload: 88000 bytes | BigInt_Hex: FFFF11223344 | gate_id: gate_1003",
        
        # NODE_E: 正常
        "[2023-10-24 01:04:22] NODE_E | Payload: 84000 bytes | BigInt_Hex: 998877665544 | gate_id: gate_1002"
    ]
    
    with open("node_logs/diagnostic_run_1.log", "w") as f:
        f.write("\n".join(logs) + "\n")

def build_turn_2():
    # 假设当前已经在 turn_2 的目录，且复制了 turn_1 产生的文件（比如 Agent的笔记）
    os.makedirs("patch_logs", exist_ok=True)
    os.makedirs("secret_shares", exist_ok=True)
    
    # 构造 patch logs
    patch_logs = [
        # NODE_A: 依旧正常
        "[2023-10-25 02:00:01] NODE_A | Payload: 45500 bytes | BigInt_Hex: 2b3c4d5e6f7a",
        
        # NODE_B: 老油条，死不悔改，依然异常
        "[2023-10-25 02:01:12] NODE_B | Payload: 87000 bytes | BigInt_Hex: 00001a2b3c4d",
        
        # NODE_D: 修好了 (流量降了，也没前缀了)
        "[2023-10-25 02:03:09] NODE_D | Payload: 82000 bytes | BigInt_Hex: 776655443322",
        
        # NODE_C: 依然是陷阱大流量无前缀
        "[2023-10-25 02:02:44] NODE_C | Payload: 145000 bytes | BigInt_Hex: 112233445566",
        
        # NODE_F: 新冒出来的异常 (流量>85000, 且带ffff)
        "[2023-10-25 02:05:33] NODE_F | Payload: 91000 bytes | BigInt_Hex: ffff98765432"
    ]
    with open("patch_logs/hotfix_run_2.log", "w") as f:
        f.write("\n".join(patch_logs) + "\n")
        
    # 构造 secret shares CSV
    # 故意让 NODE_B 和 NODE_F (两个在 turn 2 都是病态的节点) 发生碰撞
    with open("secret_shares/shares_export.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "timestamp", "share_hash"])
        writer.writerow(["NODE_A", "1698199200", "hash_a1b2c3"])
        writer.writerow(["NODE_B", "1698199205", "hash_CRITICAL_COLLISION_999"])
        writer.writerow(["NODE_C", "1698199210", "hash_d4e5f6"])
        writer.writerow(["NODE_D", "1698199215", "hash_7a8b9c"])
        writer.writerow(["NODE_E", "1698199220", "hash_112233"])
        writer.writerow(["NODE_F", "1698199225", "hash_CRITICAL_COLLISION_999"])

def build_turn_3():
    # 假设已经在 turn_3
    os.makedirs("handshake_pcap", exist_ok=True)
    
    # 构造 pcap 解析记录
    # 目标是 NODE_B 和 NODE_F (上一轮既病态又碰撞的节点)
    handshakes = [
        "Connection 1: Src=NODE_A Dst=Aggregator | Protocol: TLSv1.3 | Cipher: TLS_AES_256_GCM_SHA384",
        "Connection 2: Src=NODE_C Dst=Aggregator | Protocol: TLSv1.2 | Cipher: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        # 降级攻击 1
        "Connection 3: Src=NODE_B Dst=Aggregator | Protocol: SSLv3 | Cipher: RSA-1024-RC4-MD5 | WARNING: Deprecated suite",
        "Connection 4: Src=NODE_D Dst=Aggregator | Protocol: TLSv1.3 | Cipher: TLS_CHACHA20_POLY1305_SHA256",
        # 降级攻击 2
        "Connection 5: Src=NODE_F Dst=Aggregator | Protocol: TLSv1.0 | Cipher: TLS_RSA_WITH_DES_CBC_SHA | WARNING: Deprecated suite"
    ]
    
    with open("handshake_pcap/network_trace.txt", "w") as f:
        f.write("\n".join(handshakes) + "\n")

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
