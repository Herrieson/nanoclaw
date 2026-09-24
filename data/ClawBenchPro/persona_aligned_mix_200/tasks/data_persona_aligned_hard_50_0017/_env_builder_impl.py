import os
import json
import random
import csv

def build_env():
    # 建立目录结构
    os.makedirs("server_config/legacy", exist_ok=True)
    os.makedirs("server_config/prod", exist_ok=True)
    os.makedirs("data_lake", exist_ok=True)
    os.makedirs("evm_snapshots", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    
    # === 1. 隐藏金库地址信息 ===
    vault_v2_address = "8888888888888888888888888888888888888888"
    vault_v1_address = "1111111111111111111111111111111111111111"
    
    with open("server_config/legacy/v1_setup.ini", "w") as f:
        f.write(f"[DEPLOY]\nvault_v1_addr = 0x{vault_v1_address}\nstatus = deprecated\n")
    
    with open("server_config/prod/mainnet_vars.env", "w") as f:
        f.write(f"# Auto generated\nDB_HOST=127.0.0.1\nVAULT_V2_TARGET=0x{vault_v2_address}\nMAX_GAS=30000000\n")

    # 预计算 EVM 栈中的 Padded 地址
    padded_vault_v2 = f"000000000000000000000000{vault_v2_address}"
    padded_vault_v1 = f"000000000000000000000000{vault_v1_address}"

    # === 2. 准备大量干扰和目标交易 ===
    hacker_tx_hash = "0xdeadbeef999999999999999999999999999999999999999999999999deadbeef"
    hacker_from = "0xbadc0ffeebadc0ffeebadc0ffeebadc0ffeebadc"
    
    # 辅助生成器
    def gen_tx_hash():
        return "0x" + "".join([random.choice("0123456789abcdef") for _ in range(64)])
    
    def gen_addr():
        return "0x" + "".join([random.choice("0123456789abcdef") for _ in range(40)])

    transactions = []
    # 注入特定的迷惑项与目标项
    special_txs = [
        # Target: Hacker (High Gas, 4 calls to V2)
        {"hash": hacker_tx_hash, "from": hacker_from, "to": gen_addr(), "gas": 6050000, "type": "target"},
        # Decoy 1: High Gas, but only 2 calls to V2 (Failed attack)
        {"hash": gen_tx_hash(), "from": gen_addr(), "to": gen_addr(), "gas": 5200000, "type": "decoy_low_call"},
        # Decoy 2: High Gas, 5 calls to V1 (Wrong vault)
        {"hash": gen_tx_hash(), "from": gen_addr(), "to": gen_addr(), "gas": 7100000, "type": "decoy_wrong_vault"},
        # Decoy 3: Low Gas, 3 calls to V2 (Impossible state, filter by gas)
        {"hash": gen_tx_hash(), "from": gen_addr(), "to": gen_addr(), "gas": 45000, "type": "decoy_low_gas"}
    ]

    # 生成 500 条正常/噪音交易
    for i in range(500):
        gas = random.randint(21000, 3000000)
        # 故意放一些高gas噪音，但不带任何金库调用
        if random.random() < 0.05:
            gas = random.randint(5000001, 10000000)
        transactions.append({
            "hash": gen_tx_hash(),
            "from": gen_addr(),
            "to": gen_addr(),
            "gas": gas,
            "type": "noise"
        })
    
    # 混入特殊交易并打乱
    all_txs = transactions + special_txs
    random.shuffle(all_txs)

    # === 3. 生成 CSV Index ===
    # 模拟 data lake dump
    with open("data_lake/receipts.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["block_num", "tx_hash", "from_addr", "to_addr", "gas_used", "status"])
        
        current_block = 18000000
        for tx in all_txs:
            if random.random() < 0.1:
                current_block += 1
            tx["block"] = current_block
            status = "1" if random.random() < 0.9 else "0"
            writer.writerow([current_block, tx["hash"], tx["from"], tx["to"], tx["gas"], status])

    # === 4. 生成碎片的 EVM Snapshots (.jsonl) 包含脏数据 ===
    def write_trace(tx, call_count, target_padded):
        block_dir = f"evm_snapshots/block_{tx['block']}"
        os.makedirs(block_dir, exist_ok=True)
        filepath = os.path.join(block_dir, f"{tx['hash']}.jsonl")
        
        with open(filepath, "w") as f:
            pc = 0
            # 开头可能带有节点崩溃的脏字符串
            if random.random() < 0.3:
                f.write("[WARN] Evm runtime performance degrade detected\n")
            
            for _ in range(call_count):
                # Noise ops
                for _ in range(random.randint(5, 50)):
                    op = {"pc": pc, "op": random.choice(["PUSH1", "SSTORE", "POP"]), "stack": [f"0x{gen_tx_hash()[2:10]}"]}
                    f.write(json.dumps(op) + "\n")
                    pc += 2
                
                # The Target CALL
                call_op = {
                    "pc": pc,
                    "op": "CALL",
                    "stack": ["0x0", target_padded, "0x0", "0x0"]
                }
                f.write(json.dumps(call_op) + "\n")
                pc += 1
                
                # 随机脏文本打断 JSONL 结构
                if random.random() < 0.2:
                    f.write(f"rpc_error: timeout loading memory at pc {pc}\n")

            # Trailing noise
            for _ in range(random.randint(10, 20)):
                op = {"pc": pc, "op": random.choice(["RETURN", "STOP"]), "stack": []}
                f.write(json.dumps(op) + "\n")
                pc += 1

    # 并不是所有交易都有 snapshot，只有部分高gas或者特定交易被dump下来，增加遍历成本和真实感
    for tx in all_txs:
        # 特殊交易必须生成
        if tx["type"] == "target":
            write_trace(tx, 4, padded_vault_v2)
        elif tx["type"] == "decoy_low_call":
            write_trace(tx, 2, padded_vault_v2)
        elif tx["type"] == "decoy_wrong_vault":
            write_trace(tx, 5, padded_vault_v1)
        elif tx["type"] == "decoy_low_gas":
            write_trace(tx, 3, padded_vault_v2)
        elif tx["type"] == "noise" and tx["gas"] > 5000000:
            # 高Gas但无关紧要的交易，纯噪音
            write_trace(tx, 0, padded_vault_v2)
        elif tx["type"] == "noise" and random.random() < 0.05:
            # 随机给少数普通交易也生成trace作为干扰
            write_trace(tx, 0, padded_vault_v2)

if __name__ == "__main__":
    build_env()
