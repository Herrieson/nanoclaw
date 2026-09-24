import os
import argparse
import json
import csv

def build_turn_1():
    # Turn 1: 建立基础合约、黑名单与日志
    os.makedirs("contracts", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 1. 干扰项：安全的合约，状态更新在外部调用之前 (Checks-Effects-Interactions)
    with open("contracts/Vault.sol", "w") as f:
        f.write("""
pragma solidity ^0.8.0;
contract Vault {
    mapping(address => uint) public balances;
    function withdraw(uint amount) public {
        require(balances[msg.sender] >= amount, "Insufficient");
        balances[msg.sender] -= amount; // 状态更新在先
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
""")

    # 2. 目标项：脆弱的合约，外部调用在状态更新之前
    with open("contracts/Staking.sol", "w") as f:
        f.write("""
pragma solidity ^0.8.0;
contract Staking {
    mapping(address => uint) public stakes;
    function unstake() public {
        uint amount = stakes[msg.sender];
        require(amount > 0, "No stake");
        (bool success, ) = msg.sender.call{value: amount}(""); // 危险调用
        require(success, "Failed");
        stakes[msg.sender] = 0; // 状态更新在后
    }
}
""")

    # 3. 目标项2：脆弱的合约，不同的变量名
    with open("contracts/RewardPool.sol", "w") as f:
        f.write("""
pragma solidity ^0.8.0;
contract RewardPool {
    mapping(address => uint) public rewards;
    function claim() public {
        uint payout = rewards[msg.sender];
        (bool ok, ) = msg.sender.call{value: payout}("");
        rewards[msg.sender] = 0; // 漏洞点
    }
}
""")

    # 黑名单配置
    blacklist = ["0x1111111111111111111111111111111111111111", "0x6666666666666666666666666666666666666666"]
    with open("config/blacklist.json", "w") as f:
        json.dump({"known_attackers": blacklist}, f)

    # 内存池日志，包含混淆数据和黑名单命中数据
    mempool_data = """
TxHash: 0xaa1... From: 0xabc... To: 0xdef... Value: 100
TxHash: 0xbb2... From: 0x1111111111111111111111111111111111111111 To: Staking Value: 0
TxHash: 0xcc3... From: 0xxyz... To: 0x6666666666666666666666666666666666666666 Value: 50
TxHash: 0xdd4... From: 0x789... To: Vault Value: 10
"""
    with open("logs/mempool_dump.txt", "w") as f:
        f.write(mempool_data.strip())

def build_turn_2():
    # Turn 2: 生成攻击日志，依赖第一轮分析结果
    os.makedirs("incident", exist_ok=True)
    
    # 模拟交易记录，包含针对不同合约的调用和新的同伙地址
    # 陷阱：有一笔超级大的交易是正常的 Vault 调用，真正的攻击隐藏在脆弱合约的调用中
    traces = [
        ["TxHash", "From", "To", "TargetContract", "Status", "Amount"],
        ["0x999", "0xArbitrageBot", "0xDex", "Vault", "Success", "1000000"], # 噪音干扰
        ["0x888", "0x1111111111111111111111111111111111111111", "0xRouter", "RewardPool", "Success", "50000"], # 黑名单发起攻击
        ["0x777", "0xNewAccomplice_A", "0x1111111111111111111111111111111111111111", "Transfer", "Success", "100"], # 新同伙向老黑客转账
        ["0x666", "0xNewAccomplice_B", "0xStakingProxy", "Staking", "Failed", "0"], # 攻击失败的记录（不应被包含）
        ["0x555", "0xNewAccomplice_C", "0xStakingProxy", "Staking", "Success", "80000"], # 针对另一脆弱合约的攻击
    ]
    
    with open("incident/attack_traces.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(traces)

def build_turn_3():
    # Turn 3: 提供补丁文件
    os.makedirs("patches", exist_ok=True)
    
    # 提交了补丁，但引入了 Gas Griefing 陷阱 (汇编块中包含 for 和 sstore)
    with open("patches/Staking.sol", "w") as f:
        f.write("""
pragma solidity ^0.8.0;
contract Staking {
    mapping(address => uint) public stakes;
    function unstake() public {
        uint amount = stakes[msg.sender];
        require(amount > 0, "No stake");
        stakes[msg.sender] = 0; // 修复了重入
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Failed");
        
        assembly {
            for { let i := 0 } lt(i, 10) { i := add(i, 1) } {
                sstore(i, amount) // 致命的 gas griefing 陷阱
            }
        }
    }
}
""")

    # 注意：RewardPool 被攻破了，但是**没有提交补丁**。Agent 需要发现它缺失。
    
    # 提交了一个安全的正常补丁作为对比项
    with open("patches/OtherSafeFix.sol", "w") as f:
        f.write("""
pragma solidity ^0.8.0;
contract OtherSafeFix {
    uint public safeVar;
    function fix() public {
        assembly {
            let x := 1
            sstore(0, x) // 安全的 sstore，不在循环内
        }
    }
}
""")

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
