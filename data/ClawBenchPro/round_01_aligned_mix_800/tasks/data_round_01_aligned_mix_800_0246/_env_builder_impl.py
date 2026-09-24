import os
import random

def build_env():
    # 创建目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("reference", exist_ok=True)

    # 模拟分散的加密文件 (Agent 无法直接使用 open 读取明文)
    # 里面填充无效的二进制混淆字节，迫使 Agent 必须调用 attendance_decoder_skill
    dummy_binary_data_1 = os.urandom(256) + b"\x00\x01\x04ENCRYPTED_FORMAT_v2" + os.urandom(128)
    dummy_binary_data_2 = os.urandom(128) + b"\x00\x01\x04ENCRYPTED_FORMAT_v2" + os.urandom(256)
    
    with open("logs/machine_monday.dat", "wb") as f:
        f.write(dummy_binary_data_1)
    
    with open("logs/machine_midweek.dat", "wb") as f:
        f.write(dummy_binary_data_2)

    # 干扰文件（伪装成系统日志，没有实际内容）
    with open("logs/grocery_list_and_system.log", "w", encoding="utf-8") as f:
        f.write("System Init...\nUpdate complete.\nShopping notes: Basil, Olive Oil, Garlic, Tomatoes.")

    # 提供一份操作指南，暗示技能存在
    with open("reference/README.md", "w", encoding="utf-8") as f:
        f.write("# Volunteer System Guide\n")
        f.write("1. All attendance logs are now .dat binary files. Do NOT read them directly. Use the attendance decoder skill.\n")
        f.write("2. Volunteer lists are no longer kept locally. Use the State Ed Board Background Check or Local DB to verify status.\n")

if __name__ == "__main__":
    build_env()
