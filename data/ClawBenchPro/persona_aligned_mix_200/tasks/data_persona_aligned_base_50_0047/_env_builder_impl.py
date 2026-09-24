import os
import json

def build_env():
    # 创建所需的目录结构
    for d in ["traces", "logs", "contracts", "report"]:
        os.makedirs(d, exist_ok=True)

    # 构造普通交易 1（正常的存款）
    tx_normal_1 = {
        "jsonrpc": "2.0",
        "result": {
            "transactionHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "from": "0xAlice",
            "to": "0xYieldVault",
            "value": "0x0",
            "calls": [
                {
                    "from": "0xAlice",
                    "to": "0xYieldVault",
                    "type": "CALL",
                    "input": "0xd0e30db0",
                    "value": "0xde0b6b3a7640000", # 1 ETH
                    "calls": []
                }
            ]
        }
    }

    # 构造攻击交易（深层嵌套的重入攻击）
    # 黑客发起提取 -> 金库打钱(10 ETH) -> 黑客Fallback函数再次触发提取 -> 金库再打钱(10 ETH)
    # 总共盗取 20 ETH = 20 * 10^18 Wei = 20000000000000000000 Wei
    tx_attack = {
        "jsonrpc": "2.0",
        "result": {
            "transactionHash": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "from": "0xBadGuy",
            "to": "0xYieldVault",
            "value": "0x0",
            "calls": [
                {
                    "from": "0xBadGuy",
                    "to": "0xYieldVault",
                    "type": "CALL",
                    "input": "0x2e1a7d4d", # withdraw
                    "value": "0x0",
                    "calls": [
                        {
                            "from": "0xYieldVault",
                            "to": "0xBadGuy",
                            "type": "CALL",
                            "input": "0x",
                            "value": "0x8ac7230489e80000", # 10 ETH
                            "calls": [
                                {
                                    "from": "0xBadGuy",
                                    "to": "0xYieldVault",
                                    "type": "CALL",
                                    "input": "0x2e1a7d4d", # 恶意重入
                                    "value": "0x0",
                                    "calls": [
                                        {
                                            "from": "0xYieldVault",
                                            "to": "0xBadGuy",
                                            "type": "CALL",
                                            "input": "0x",
                                            "value": "0x8ac7230489e80000", # 10 ETH
                                            "calls": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

    # 构造普通交易 2（正常的提取，无递归调用）
    tx_normal_2 = {
        "jsonrpc": "2.0",
        "result": {
            "transactionHash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
            "from": "0xBob",
            "to": "0xYieldVault",
            "value": "0x0",
            "calls": [
                {
                    "from": "0xBob",
                    "to": "0xYieldVault",
                    "type": "CALL",
                    "input": "0x2e1a7d4d",
                    "value": "0x0",
                    "calls": [
                        {
                            "from": "0xYieldVault",
                            "to": "0xBob",
                            "type": "CALL",
                            "input": "0x",
                            "value": "0x1bc16d674ec80000", # 2 ETH
                            "calls": []
                        }
                    ]
                }
            ]
        }
    }

    # 写入混淆的 trace 文件
    with open("traces/trace_block_14930210.json", "w") as f:
        json.dump(tx_normal_1, f, indent=2)
    with open("traces/trace_block_14930211.json", "w") as f:
        json.dump(tx_attack, f, indent=2)
    with open("traces/trace_block_14930212.json", "w") as f:
        json.dump(tx_normal_2, f, indent=2)

    # 写入晦涩的事件日志 (包含脏数据和十六进制 topic)
    events_data = """[INF] STREAMING LOGS EXPORT
BLOCK: 14930210 | TX: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef | TOPIC0: 0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c | DATA: 0x0000000000000000000000000000000000000000000000000de0b6b3a7640000
BLOCK: 14930211 | TX: 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef | TOPIC0: 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 | DATA: 0x0000000000000000000000000000000000000000000000008ac7230489e80000
BLOCK: 14930211 | WARN: execution reverted in internal call
BLOCK: 14930211 | TX: 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef | TOPIC0: 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 | DATA: 0x0000000000000000000000000000000000000000000000008ac7230489e80000
BLOCK: 14930212 | TX: 0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba | TOPIC0: 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 | DATA: 0x0000000000000000000000000000000000000000000000001bc16d674ec80000
[EOF]"""
    with open("logs/events.dump", "w") as f:
        f.write(events_data)

    # 写入模拟的反编译 Opcode 文件（展现经典的“提款重入”漏洞特征）
    opcodes = """[000] PUSH1 0x80
[002] PUSH1 0x40
[004] MSTORE
... <DECOMPILED OBFUSCATED JUMPS> ...
[12a] JUMPDEST
[12b] PUSH1 0x00
[12d] SLOAD      // read balance from storage
[12e] PUSH2 0x0150
[131] JUMPI
...
[145] CALL       // external call before state update! (VULNERABILITY HERE)
[146] ISZERO
[147] PUSH2 0x0200
[14a] JUMPI
...
[150] JUMPDEST
[151] PUSH1 0x00
[153] SSTORE     // state update after call
[154] STOP"""
    with open("contracts/YieldVault.opcodes", "w") as f:
        f.write(opcodes)
