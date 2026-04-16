import os
import json
import base64
import random

def setup_environment():
    base_path = "assets/data_492"
    os.makedirs(base_path, exist_ok=True)

    # 1. 制造混乱的文件系统
    subdirs = ["logs", "scripts", "temp", "archive/old_backups"]
    for sd in subdirs:
        os.makedirs(os.path.join(base_path, sd), exist_ok=True)

    # 2. 隐藏的密钥 (在乱七八糟的脚本里)
    script_content = """
# Viktor's experimental scraper
# Note to self: The XOR key for the Aetheron packets is 'VOYAGER7'
# I need to remember to buy more vinyl records...
import os

def main():
    print("Testing connection to internal node...")
    # ... dummy code ...
    pass
"""
    with open(os.path.join(base_path, "scripts/test_node_v2.py"), "w") as f:
        f.write(script_content)

    # 3. 伪造加密的“流量数据” (Base64 + XOR)
    # 原始数据: {"user_id": "UX-9928", "gps": "40.7580, -73.9855", "project": "Argus-Eye"}
    raw_data = '{"user_id": "UX-9928", "gps": "40.7580, -73.9855", "project": "Argus-Eye"}'
    key = "VOYAGER7"
    
    def xor_cipher(data, key):
        return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

    encrypted_data = xor_cipher(raw_data, key)
    encoded_payload = base64.b64encode(encrypted_data.encode()).decode()

    # 4. 生成混淆的日志文件
    log_entries = [
        "2023-10-27 14:20:01 INFO: System Heartbeat OK",
        "2023-10-27 14:21:45 WARN: Unrecognized packet on port 8888",
        f"2023-10-27 14:22:10 TRACE: Packet Dump: {encoded_payload}",
        "2023-10-27 14:25:00 ERROR: Connection reset by peer"
    ]
    
    with open(os.path.join(base_path, "logs/syslog.log"), "w") as f:
        f.write("\n".join(log_entries))

    # 5. 干扰项
    with open(os.path.join(base_path, "temp/notes.txt"), "w") as f:
        f.write("Need to pay the electricity bill. Also, check out the new synth-pop album.")

if __name__ == "__main__":
    setup_environment()
