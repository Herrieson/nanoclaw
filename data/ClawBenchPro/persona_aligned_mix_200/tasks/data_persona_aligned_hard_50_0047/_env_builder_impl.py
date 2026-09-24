import os
import json
import random
import uuid

def build_env():
    # 1. 废土环境目录初始化
    base_dirs = [
        "logs/server/2023",
        "logs/server/2024",
        "contracts_repo/bin",
        "report"
    ]
    rpc_base = "rpc_dumps/node_01"
    
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)
    
    for i in range(1, 21): # 生成 20 个区块目录
        os.makedirs(f"{rpc_base}/block_{15000000 + i}", exist_ok=True)

    # 2. 隐藏真实金库地址及噪音日志
    vault_address = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
    dummy_vault = "0x000000000000000000000000000000000000dead"
    
    log_content = f"""[2024-05-10 10:11:22] WARN node sync delayed
[2024-05-10 10:12:01] INFO [Deployer] Deploying YieldVault_v2... Success: {dummy_vault}
[2024-05-10 10:15:33] ERROR p2p connection dropped
[2024-05-11 14:00:21] INFO [Deployer] Emergency upgrade initialized. Deploying YieldVault_v3... 
[2024-05-11 14:00:45] INFO [Deployer] YieldVault_v3 Contract successfully deployed at {vault_address} (proxy bypassed).
[2024-05-11 14:10:00] INFO RPC endpoints alive.
"""
    with open("logs/server/2024/deployments_prod.log", "w") as f:
        f.write(log_content)
        
    for i in range(5):
        with open(f"logs/server/2024/garbage_sys_{i}.log", "w") as f:
            f.write("".join([f"Trace {uuid.uuid4()} timeout.\n" for _ in range(50)]))

    # 3. 构造 Trace 生成辅助函数
    def make_call(frm, to, val, calls=None):
        return {"from": frm, "to": to, "type": "CALL", "value": val, "calls": calls or []}

    def write_tx(block, tx_hash, status, action):
        path = f"{rpc_base}/block_{block}/tx_{tx_hash[:10]}.json"
        tx_data = {
            "jsonrpc": "2.0",
            "result": {
                "transactionHash": tx_hash,
                "status": status, # "0x1" for success, "0x0" for revert
                "action": action
            }
        }
        with open(path, "w") as f:
            json.dump(tx_data, f, indent=2)

    # 4. 批量生成噪音交易 (普通转账、套利，不会嵌套)
    for block in range(15000001, 15000021):
        for _ in range(15): # 每个区块 15 笔随机交易
            tx_h = "0x" + uuid.uuid4().hex + uuid.uuid4().hex
            frm = "0x" + uuid.uuid4().hex[:40]
            to = "0x" + uuid.uuid4().hex[:40]
            val = hex(random.randint(0, 10**18))
            write_tx(block, tx_h, "0x1", make_call(frm, to, val))

    # 5. 构造特定类型的交易
    attacker = "0xbadc0de000000000000000000000000000000000"
    
    # [干扰项 1]：针对假金库 (v2) 的重入攻击 (成功，但不是 v3)
    fake_attack_tx = "0x1111111111111111111111111111111111111111111111111111111111111111"
    fake_attack = make_call(attacker, dummy_vault, "0x0", [
        make_call(dummy_vault, attacker, "0xde0b6b3a7640000", [ # 1 ETH
            make_call(attacker, dummy_vault, "0x0", [
                make_call(dummy_vault, attacker, "0xde0b6b3a7640000")
            ])
        ])
    ])
    write_tx(15000005, fake_attack_tx, "0x1", fake_attack)

    # [干扰项 2]：针对真金库 (v3) 的重入攻击，但是执行失败 (status: "0x0", Reverted)
    reverted_attack_tx = "0x2222222222222222222222222222222222222222222222222222222222222222"
    reverted_attack = make_call(attacker, vault_address, "0x0", [
        make_call(vault_address, attacker, "0x8ac7230489e80000", [ # 10 ETH
            make_call(attacker, vault_address, "0x0", [
                make_call(vault_address, attacker, "0x8ac7230489e80000")
            ])
        ])
    ])
    write_tx(15000008, reverted_attack_tx, "0x0", reverted_attack)

    # [目标项]：针对真金库 (v3) 的真实重入攻击 (成功)
    # 计算：递归 4 次，每次窃取 5.5 ETH
    # 5.5 ETH = 5,500,000,000,000,000,000 Wei = 0x4C53503D6FBDC000
    # 共窃取 22 ETH = 22,000,000,000,000,000,000 Wei (十进制: 22000000000000000000)
    target_tx = "0xdeadbeef888888888888888888888888888888888888888888888888deadbeef"
    steal_val_hex = "0x4C53503D6FBDC000" 
    
    real_attack = make_call(attacker, vault_address, "0x0", [
        make_call(vault_address, attacker, steal_val_hex, [
            make_call(attacker, vault_address, "0x0", [
                make_call(vault_address, attacker, steal_val_hex, [
                    make_call(attacker, vault_address, "0x0", [
                        make_call(vault_address, attacker, steal_val_hex, [
                            make_call(attacker, vault_address, "0x0", [
                                make_call(vault_address, attacker, steal_val_hex)
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])
    write_tx(15000014, target_tx, "0x1", real_attack)

    # [干扰项 3]：针对真金库的正常大额提取（无重入嵌套，只有单次转账出去）
    normal_withdraw_tx = "0x3333333333333333333333333333333333333333333333333333333333333333"
    normal_withdraw = make_call("0xwhale", vault_address, "0x0", [
        make_call(vault_address, "0xwhale", "0x3635c9adc5dea00000") # 1000 ETH
    ])
    write_tx(15000015, normal_withdraw_tx, "0x1", normal_withdraw)
