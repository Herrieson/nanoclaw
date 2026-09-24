import os
import json
import random

def build_env():
    # Create necessary directories
    os.makedirs("traces", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    
    vault_address = "8888888888888888888888888888888888888888"
    padded_vault = f"000000000000000000000000{vault_address}"
    
    # Generate some noise logs
    with open("traces/node_panic_dump.log", "w") as f:
        f.write("FATAL ERROR: evm execution panicked at src/core/vm.rs:109\n")
        f.write("Hex dump: \n")
        for _ in range(20):
            f.write("".join([random.choice("0123456789abcdef") for _ in range(128)]) + "\n")

    def generate_struct_logs(call_count, target_address_padded, noise_level=50):
        logs = []
        pc = 0
        for _ in range(call_count):
            # Insert noise operations
            for _ in range(random.randint(5, noise_level)):
                logs.append({
                    "pc": pc,
                    "op": random.choice(["PUSH1", "SSTORE", "JUMPDEST", "MSTORE", "SWAP1", "POP"]),
                    "gas": random.randint(100, 5000),
                    "stack": [f"0x{random.choice('0123456789abcdef') * 64}"]
                })
                pc += 2
            
            # Insert the specific CALL
            logs.append({
                "pc": pc,
                "op": "CALL",
                "gas": random.randint(10000, 50000),
                "stack": ["0x0", f"0x{target_address_padded}", "0x0", "0x0"]
            })
            pc += 1
            
        # Add trailing noise
        for _ in range(random.randint(10, 20)):
            logs.append({
                "pc": pc,
                "op": random.choice(["RETURN", "STOP", "REVERT"]),
                "gas": 0,
                "stack": []
            })
            pc += 1
            
        return logs

    # Transaction 1: Normal transaction, small gas, no target calls
    tx1 = {
        "transactionHash": "0x1111111111111111111111111111111111111111111111111111111111111111",
        "from": "0xaaaa1111aaaa1111aaaa1111aaaa1111aaaa1111",
        "to": "0xcccccccccccccccccccccccccccccccccccccccc",
        "receipt": {"status": "0x1", "gasUsed": 45000},
        "structLogs": generate_struct_logs(1, "000000000000000000000000cccccccccccccccccccccccccccccccccccccccc")
    }
    with open("traces/tx_trace_01.json", "w") as f:
        json.dump(tx1, f, indent=2)

    # Transaction 2: High gas, but only 2 calls to vault (Failed attack attempt)
    tx2 = {
        "transactionHash": "0x2222222222222222222222222222222222222222222222222222222222222222",
        "from": "0xbbbb2222bbbb2222bbbb2222bbbb2222bbbb2222",
        "to": "0xdddddddddddddddddddddddddddddddddddddddd",
        "receipt": {"status": "0x0", "gasUsed": 6500000},
        "structLogs": generate_struct_logs(2, padded_vault)
    }
    with open("traces/tx_trace_02.json", "w") as f:
        json.dump(tx2, f, indent=2)

    # Transaction 3: The actual exploit
    tx3 = {
        "transactionHash": "0xdeadbeef999999999999999999999999999999999999999999999999deadbeef",
        "from": "0xbadc0ffeebadc0ffeebadc0ffeebadc0ffeebadc",
        "to": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "receipt": {"status": "0x1", "gasUsed": 5000001},
        "structLogs": generate_struct_logs(4, padded_vault, noise_level=100)
    }
    with open("traces/tx_trace_03.json", "w") as f:
        json.dump(tx3, f, indent=2)

    # Transaction 4: High gas, 5 calls, but wrong vault address
    tx4 = {
        "transactionHash": "0x4444444444444444444444444444444444444444444444444444444444444444",
        "from": "0xdddd4444dddd4444dddd4444dddd4444dddd4444",
        "to": "0xffffffffffffffffffffffffffffffffffffffff",
        "receipt": {"status": "0x1", "gasUsed": 7200000},
        "structLogs": generate_struct_logs(5, "0000000000000000000000007777777777777777777777777777777777777777")
    }
    with open("traces/tx_trace_04.json", "w") as f:
        json.dump(tx4, f, indent=2)

    # Transaction 5: Low gas, 3 calls to vault (Impossible normal path, filtered by gas)
    tx5 = {
        "transactionHash": "0x5555555555555555555555555555555555555555555555555555555555555555",
        "from": "0xeeee5555eeee5555eeee5555eeee5555eeee5555",
        "to": "0x1111111111111111111111111111111111111111",
        "receipt": {"status": "0x1", "gasUsed": 21000},
        "structLogs": generate_struct_logs(3, padded_vault)
    }
    with open("traces/tx_trace_05.json", "w") as f:
        json.dump(tx5, f, indent=2)

if __name__ == "__main__":
    build_env()
