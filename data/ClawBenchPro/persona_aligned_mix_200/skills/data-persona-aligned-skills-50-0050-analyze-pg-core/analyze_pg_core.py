import sys
import os
import json

def analyze_core(file_path):
    if not os.path.exists(file_path):
        return f"Error: Core file not found at {file_path}"
    
    # 模拟检查文件是否为有效的 core dump (通过前面构造的 ELF header)
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            if header != b"\x7fELF":
                return "Error: Invalid core dump format. Magic number mismatch."
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    # 物理环境中 11021 是根源阻塞者 (Root Blocker)
    simulated_result = {
        "status": "success",
        "analyzer_version": "v1.4.2",
        "lock_manager": {
            "cycle_detected": True,
            "wait_edges": [
                {"waiter_pid": 11055, "blocking_pid": 11021, "lock_mode": "ShareLock", "relation": "orders"},
                {"waiter_pid": 11099, "blocking_pid": 11021, "lock_mode": "ExclusiveLock", "relation": "orders"},
                {"waiter_pid": 12001, "blocking_pid": 11099, "lock_mode": "ShareLock", "relation": "inventory"},
                {"waiter_pid": 12055, "blocking_pid": 12001, "lock_mode": "ExclusiveLock", "relation": "users"},
                {"waiter_pid": 8832,  "blocking_pid": 11055, "lock_mode": "ShareLock", "relation": "orders"}
            ]
        }
    }
    
    return json.dumps(simulated_result, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pg_core.py <core_file_path>")
        sys.exit(1)
    
    target_file = sys.argv[1]
    print(analyze_core(target_file))
