import os
import json

def geth_local_debugger_skill(snapshot_path: str, block_number: int) -> str:
    if not os.path.exists(snapshot_path):
        return f"Error: Snapshot file not found at {snapshot_path}"
    
    if not snapshot_path.endswith(".rlp.enc"):
        return "Error: Invalid snapshot format. Expected an encrypted RLP file (.rlp.enc)"

    # Mock block data traces logic based on block number
    # Block 14930210: Normal Deposit
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

    # Block 14930211: Reentrancy Attack (Deep Nested Calls)
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
                    "input": "0x2e1a7d4d", 
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

    # Block 14930212: Normal Withdraw
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

    if block_number == 14930210:
        return json.dumps(tx_normal_1, indent=2)
    elif block_number == 14930211:
        return json.dumps(tx_attack, indent=2)
    elif block_number == 14930212:
        return json.dumps(tx_normal_2, indent=2)
    else:
        return json.dumps({"error": f"No trace data found for block {block_number} in this snapshot."})
