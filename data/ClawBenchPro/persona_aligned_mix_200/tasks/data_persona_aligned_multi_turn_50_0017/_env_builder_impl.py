import os
import argparse
import json
import csv

def build_turn_1():
    # 构造目录结构
    os.makedirs("tx_logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    # 1. 白名单配置
    with open("config/whitelist.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "entity"])
        writer.writerow(["0xWhiteListAAABBBCCC", "Aave_Flashloan"])
        writer.writerow(["0xWhiteListDDDDEEEE", "MakerDAO_Oracle"])

    # 2. 交易日志 (Mock 数据陷阱)
    # H1: 真正的黑客 (同区块调用 4 次, 无特殊标识)
    # H2: 合法套利但Turn1看起来像黑客 (同区块调用 3次, 但 data 前缀是 0xabc)
    # W1: 白名单 (同区块调用 5次, 但是在白名单里)
    # N1: 普通用户 (调用 1次)
    
    logs = [
        # Block 1001
        {"hash": "0xTx_001", "sender": "0xWhiteListAAABBBCCC", "block_number": 1001, "gas_used": 150000, "data": "0x1234", "value": 100},
        {"hash": "0xTx_002", "sender": "0xWhiteListAAABBBCCC", "block_number": 1001, "gas_used": 150000, "data": "0x1234", "value": 100},
        {"hash": "0xTx_003", "sender": "0xWhiteListAAABBBCCC", "block_number": 1001, "gas_used": 150000, "data": "0x1234", "value": 100},
        {"hash": "0xTx_004", "sender": "0xHack1_BadGuy999", "block_number": 1001, "gas_used": 350000, "data": "0x9999ffff", "value": 5000},
        {"hash": "0xTx_005", "sender": "0xHack1_BadGuy999", "block_number": 1001, "gas_used": 340000, "data": "0x9999ffff", "value": 5000},
        {"hash": "0xTx_006", "sender": "0xHack1_BadGuy999", "block_number": 1001, "gas_used": 330000, "data": "0x9999ffff", "value": 5000},
        {"hash": "0xTx_007", "sender": "0xHack1_BadGuy999", "block_number": 1001, "gas_used": 320000, "data": "0x9999ffff", "value": 5000},
        # Block 1002
        {"hash": "0xTx_008", "sender": "0xNormalUser_888", "block_number": 1002, "gas_used": 21000, "data": "0x00", "value": 50},
        {"hash": "0xTx_009", "sender": "0xHack2_Arbitrage", "block_number": 1002, "gas_used": 120000, "data": "0xabcdef0011", "value": 800},
        {"hash": "0xTx_010", "sender": "0xHack2_Arbitrage", "block_number": 1002, "gas_used": 120000, "data": "0xabcdef0022", "value": 800},
        {"hash": "0xTx_011", "sender": "0xHack2_Arbitrage", "block_number": 1002, "gas_used": 120000, "data": "0xabcdef0033", "value": 800},
    ]

    # 为了增加复杂度，存入嵌套结构
    block_data = {
        "network": "Ethereum Mainnet",
        "timestamp": 1690000000,
        "transactions": logs
    }
    with open("tx_logs/blocks_export.json", "w") as f:
        json.dump(block_data, f, indent=4)

def build_turn_2():
    # 模拟新轮次的文件环境
    os.makedirs("memos", exist_ok=True)
    os.makedirs("bridge_logs", exist_ok=True)

    # 1. 注入合规新规
    with open("memos/new_arbitrage_rules.md", "w") as f:
        f.write("# 紧急合规通知\n\n")
        f.write("经查，部分 MEV 机器人和清算节点虽然不在白名单内，但其行为合规。\n")
        f.write("判定标准：若交易记录的 `data` 字段以十六进制 `0xabc` 作为前缀，则属于合法的多重路由清算行为，不得将其定性为重入攻击！\n")

    # 2. 注入跨链桥日志
    bridge_records = [
        {"tx_hash": "0xb_1", "source_address": "0xHack1_BadGuy999", "dest_address": "0xCrossChain_Dark01", "amount": 10000, "chain_id": 56},
        {"tx_hash": "0xb_2", "source_address": "0xHack1_BadGuy999", "dest_address": "0xCrossChain_Dark01", "amount": 10000, "chain_id": 56},
        {"tx_hash": "0xb_3", "source_address": "0xHack2_Arbitrage", "dest_address": "0xCrossChain_ArbDest", "amount": 2400, "chain_id": 137},
        {"tx_hash": "0xb_4", "source_address": "0xNormalUser_888", "dest_address": "0xCrossChain_Norm", "amount": 50, "chain_id": 10}
    ]
    with open("bridge_logs/cross_chain_events.json", "w") as f:
        json.dump(bridge_records, f, indent=4)

def build_turn_3():
    # 模拟新轮次的文件环境
    os.makedirs("deployments", exist_ok=True)
    os.makedirs("bytecode", exist_ok=True)

    # 1. 部署记录
    with open("deployments/deploy_traces.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["contract_address", "deployer", "timestamp"])
        writer.writerow(["0xEvilContract_AA1", "0xCrossChain_Dark01", "1690008000"])
        writer.writerow(["0xEvilContract_BB2", "0xCrossChain_Dark01", "1690008100"])
        writer.writerow(["0xSafeContract_CC3", "0xCrossChain_ArbDest", "1690008200"])
        writer.writerow(["0xRandomContract_DD4", "0xUnknownHackerXYZ", "1690008300"])

    # 2. 字节码文件
    # AA1 包含 F4 (DELEGATECALL), 是黑客的老鼠洞
    with open("bytecode/0xEvilContract_AA1.hex", "w") as f:
        f.write("608060405234801561001057600080fd5b506004361061002b5760003560e01c80630000000014610030575b600080fd5b61004a6004803603810190808035906020019092919050505061004c565b005b806000803e6000805cf4156064573d6000803e3d6000fd5b3d6000f3fea164736f6c6343000811000a")
    
    # BB2 正常字节码，用来测试干扰
    with open("bytecode/0xEvilContract_BB2.hex", "w") as f:
        f.write("608060405234801561001057600080fd5b506004361061002b5760003560e01c80630000000014610030575b600080fd5b61004a6004803603810190808035906020019092919050505061004c565b005b806000803e6000805c55156064573d6000803e3d6000fd5b3d6000f3fea164736f6c6343000811000a")

    # CC3 合法套利者部署的正常合约
    with open("bytecode/0xSafeContract_CC3.hex", "w") as f:
        f.write("6080604052600080fdfea164736f6c6343000811000a")
        
    # DD4 带有 FF (SELFDESTRUCT) 但 deployer 不是洗钱目标地址
    with open("bytecode/0xRandomContract_DD4.hex", "w") as f:
        f.write("6080604052600080fffea164736f6c6343000811000a")

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
