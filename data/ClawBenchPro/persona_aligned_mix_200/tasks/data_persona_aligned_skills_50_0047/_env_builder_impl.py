import os
import json
import base64

def build_env():
    # 创建所需的目录结构
    for d in ["traces", "logs", "contracts", "report"]:
        os.makedirs(d, exist_ok=True)

    # 1. 构造一个无法直接读取的假加密 RLP 节点快照文件
    # 真实数据已经被抽离到 geth_local_debugger_skill.py 中进行解析返回
    dummy_encrypted_data = b"ENCRYPTED_GETH_RLP_SNAPSHOT_HEADER_0x9A4B... \n" + os.urandom(1024)
    with open("traces/node_snapshot.rlp.enc", "wb") as f:
        f.write(base64.b64encode(dummy_encrypted_data))

    # 2. 写入晦涩的事件日志 (包含脏数据和十六进制 topic，作为区块号的线索来源)
    events_data = """[INF] STREAMING LOGS EXPORT
BLOCK: 14930210 | TX: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef | TOPIC0: 0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c | DATA: 0x0000000000000000000000000000000000000000000000000de0b6b3a7640000
BLOCK: 14930211 | TX: 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef | TOPIC0: 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 | DATA: 0x0000000000000000000000000000000000000000000000008ac7230489e80000
BLOCK: 14930211 | WARN: execution reverted in internal call
BLOCK: 14930211 | TX: 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef | TOPIC0: 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 | DATA: 0x0000000000000000000000000000000000000000000000008ac7230489e80000
BLOCK: 14930212 | TX: 0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba | TOPIC0: 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 | DATA: 0x0000000000000000000000000000000000000000000000001bc16d674ec80000
[EOF]"""
    with open("logs/events.dump", "w") as f:
        f.write(events_data)

    # 3. 写入模拟的反编译 Opcode 文件（展现经典的“提款重入”漏洞特征）
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

if __name__ == "__main__":
    build_env()
