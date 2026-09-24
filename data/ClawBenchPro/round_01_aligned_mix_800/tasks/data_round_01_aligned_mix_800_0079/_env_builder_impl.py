import os
import argparse
import json
import random

def build_turn_1():
    # 核心代码库模拟：包含多个微服务源码
    services = ["auth-module", "payment-gateway", "data-aggregator"]
    os.makedirs("src", exist_ok=True)
    
    for svc in services:
        svc_path = os.path.join("src", svc)
        os.makedirs(svc_path, exist_ok=True)
        # 写入混有注释、复杂逻辑和隐患的代码
        with open(os.path.join(svc_path, "core.py"), "w") as f:
            f.write(f'# Service: {svc}\n')
            f.write('import hashlib\n\n')
            f.write('def process_request(data):\n')
            if svc == "auth-module":
                f.write('    # Legacy: Using MD5 for quick hash, must be replaced later\n')
                f.write('    token = hashlib.md5(data.encode()).hexdigest()\n')
                f.write('    return {"status": "ok", "token": token}\n')
            elif svc == "payment-gateway":
                f.write('    # Dependency: requires auth-module token validation\n')
                f.write('    if len(data.get("token", "")) < 32:\n')
                f.write('        return {"error": "invalid"}\n')
                f.write('    return {"amount": 100, "currency": "USD"}\n')
            else:
                f.write('    return {"data": "processed"}\n')

    # 遗留资产清单（干扰项）
    with open("legacy_inventory.json", "w") as f:
        json.dump({
            "obsolete_servers": ["SRV-001", "SRV-099"],
            "tech_stack": ["Python 2.7", "Python 3.10"],
            "critical_dependencies": ["auth-module", "payment-gateway"]
        }, f, indent=4)

def build_turn_2():
    # 模拟外部合规文件更新
    os.makedirs("compliance", exist_ok=True)
    with open("compliance/security_policy_v2.txt", "w") as f:
        f.write("SECURITY POLICY VERSION 2.0\n")
        f.write("---------------------------\n")
        f.write("1. All cryptographic hashing must use SHA-256 or higher.\n")
        f.write("2. MD5 is strictly prohibited for sensitive data tokens.\n")
        f.write("3. Deprecated modules must be flagged in a separate migration-plan.")

def build_turn_3():
    # 注入突发错误日志，指向受影响的服务
    os.makedirs("logs", exist_ok=True)
    with open("logs/runtime_error.log", "w") as f:
        f.write("2023-10-27 10:15:02 ERROR: Validation failed in payment-gateway. Reason: Token format mismatch.\n")
        f.write("2023-10-27 10:16:45 WARN: auth-module response time exceeding 200ms.\n")

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
