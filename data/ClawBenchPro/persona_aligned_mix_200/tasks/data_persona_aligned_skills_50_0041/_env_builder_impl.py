import os
import random

def build_env():
    os.makedirs("sandbox", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    # 1. 构造加密/伪专有格式的 Sandbox Trace 数据 (取代易读的 txt，迫使 Agent 使用 TAS API)
    # 写入一些无意义的随机二进制数据模拟加密存储，实际答案由 LLM mock 给出
    with open("sandbox/trace.dat", "wb") as f:
        f.write(b"CUCKOO_TRACE_V3_ENCRYPTED_DATA\x00")
        f.write(os.urandom(1024 * 50)) # 50KB random bytes

    # 2. 构造真正的二进制内存 Dump 文件 (取代十六进制文本，迫使 Agent 使用特定的扫描工具)
    # 大小设定为 64KB
    dump_size = 64 * 1024
    mem_data = bytearray(os.urandom(dump_size))
    
    # 埋入特征码（魔术字 BA AD F0 0D 后面紧跟 16 字节真实特征码）
    magic_bytes = bytes.fromhex("BAADF00D")
    payload_signature = bytes.fromhex("5C7A8E1F2B3D4C5A6B7C8D9EAFB0C1D2")
    
    # 将其埋在一个特定的偏移位置，比如 0x4B3A
    inject_offset = 0x4B3A
    mem_data[inject_offset : inject_offset + 4] = magic_bytes
    mem_data[inject_offset + 4 : inject_offset + 4 + 16] = payload_signature
    
    # 为了增加迷惑性，随机再写入一个假的只包含部分的特征
    fake_offset = 0x1A20
    mem_data[fake_offset : fake_offset + 4] = bytes.fromhex("BAADF000") # 差一点点
    mem_data[fake_offset + 4 : fake_offset + 4 + 16] = os.urandom(16)
    
    with open("dumps/raw_mem.bin", "wb") as f:
        f.write(mem_data)

if __name__ == "__main__":
    build_env()
