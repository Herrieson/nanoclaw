import os
import argparse
import json
import csv

def write_hex_dump(filename, target_offset, payload_hex_list):
    """生成模拟的十六进制内存转储文本"""
    with open(filename, "w", encoding="utf-8") as f:
        for offset in range(0x1000, 0x9000, 16):
            if offset == target_offset:
                hex_str = " ".join([f"{b:02X}" for b in payload_hex_list])
            else:
                hex_str = " ".join(["00"] * 16)
            f.write(f"0x{offset:08X}: {hex_str}\n")

def build_turn_1():
    os.makedirs("sandbox_logs", exist_ok=True)
    os.makedirs("mem_dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 正常干扰日志
    trace_01 = [
        {"pid": 1024, "api": "OpenFile", "args": {"file": "C:\\Windows\\System32\\kernel32.dll"}},
        {"pid": 1024, "api": "RegOpenKeyEx", "args": {"key": "HKLM\\Software\\Classes"}},
        {"pid": 1024, "api": "VirtualAllocEx", "args": {"target_pid": 1024, "address": "0x2000", "size": 256}}
    ]
    with open("sandbox_logs/trace_01.json", "w") as f:
        json.dump(trace_01, f, indent=2)

    # 真正的恶意进程日志 (Turn 1)
    trace_02 = [
        {"pid": 8820, "api": "CreateFile", "args": {"file": "malware_dropper.exe"}},
        {"pid": 8820, "api": "RegSetValueEx", "args": {"key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\CryptoNova", "value": "malware.exe"}},
        {"pid": 8820, "api": "VirtualAllocEx", "args": {"target_pid": 4433, "address": "0x4000", "size": 1024}},
        {"pid": 8820, "api": "WriteProcessMemory", "args": {"target_pid": 4433, "address": "0x4000", "size": 16}},
        {"pid": 8820, "api": "CreateRemoteThread", "args": {"target_pid": 4433, "address": "0x4000"}}
    ]
    with open("sandbox_logs/trace_02.json", "w") as f:
        json.dump(trace_02, f, indent=2)

    # 生成对应的内存转储
    # Payload T1: 44 45 41 44 42 45 45 46 43 41 46 45 42 41 42 45 (DEADBEEFCAFEBABE)
    t1_payload = [0x44, 0x45, 0x41, 0x44, 0x42, 0x45, 0x45, 0x46, 0x43, 0x41, 0x46, 0x45, 0x42, 0x41, 0x42, 0x45]
    write_hex_dump("mem_dumps/proc_1024.dmp", 0x2000, [0x90]*16)
    write_hex_dump("mem_dumps/proc_4433.dmp", 0x4000, t1_payload)


def build_turn_2():
    # 环境已经被拷贝，我们直接在已有目录下注入新的数据
    # 诱饵进程：复用了相同的注册表项 和 相同的Payload
    trace_decoy = [
        {"pid": 1111, "api": "VirtualAllocEx", "args": {"target_pid": 2222, "address": "0x5000", "size": 1024}},
        {"pid": 1111, "api": "WriteProcessMemory", "args": {"target_pid": 2222, "address": "0x5000", "size": 16}},
        {"pid": 1111, "api": "CreateRemoteThread", "args": {"target_pid": 2222, "address": "0x5000"}},
        {"pid": 1111, "api": "RegSetValueEx", "args": {"key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\CryptoNova", "value": "decoy.exe"}}
    ]
    with open("sandbox_logs/trace_03_decoy.json", "w") as f:
        json.dump(trace_decoy, f, indent=2)

    # 真正的新变种：全新的注册表项 和 全新的Payload
    trace_real = [
        {"pid": 5510, "api": "VirtualAllocEx", "args": {"target_pid": 9921, "address": "0x8000", "size": 1024}},
        {"pid": 5510, "api": "WriteProcessMemory", "args": {"target_pid": 9921, "address": "0x8000", "size": 16}},
        {"pid": 5510, "api": "CreateRemoteThread", "args": {"target_pid": 9921, "address": "0x8000"}},
        {"pid": 5510, "api": "RegSetValueEx", "args": {"key": "HKLM\\System\\CurrentControlSet\\Services\\WinDefend\\ImagePath", "value": "hijacked.exe"}}
    ]
    with open("sandbox_logs/trace_04_real.json", "w") as f:
        json.dump(trace_real, f, indent=2)

    # Payload T1 重复 (Decoy)
    t1_payload = [0x44, 0x45, 0x41, 0x44, 0x42, 0x45, 0x45, 0x46, 0x43, 0x41, 0x46, 0x45, 0x42, 0x41, 0x42, 0x45]
    write_hex_dump("mem_dumps/proc_2222.dmp", 0x5000, t1_payload)

    # Payload T2 全新 (BAADF00D1234567890ABCDEF00000000)
    t2_payload = [0xBA, 0xAD, 0xF0, 0x0D, 0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF, 0x00, 0x00, 0x00, 0x00]
    write_hex_dump("mem_dumps/proc_9921.dmp", 0x8000, t2_payload)


def build_turn_3():
    os.makedirs("network_pcap", exist_ok=True)
    os.makedirs("crypto_config", exist_ok=True)

    # 构建恶意通信流量
    # 这里要保证 PID 5510 的 Heartbeat 后面紧跟的是真实的异或密钥
    traffic_data = [
        ["Timestamp", "PID", "Type", "Data"],
        ["10:00:01", "1024", "DNS_Req", "google.com"],
        ["10:00:02", "1111", "Heartbeat", "OK"],
        ["10:00:03", "1111", "KeyExchange", "0x11"],  # 诱饵进程的错误密钥
        ["10:00:05", "5510", "Heartbeat", "OK"],
        ["10:00:06", "5510", "KeyExchange", "0x5A"],  # 真实进程的正确密钥 XOR Key = 0x5A
        ["10:00:08", "8820", "Heartbeat", "OK"],
        ["10:00:09", "8820", "KeyExchange", "0xFF"]   # T1进程的过期密钥
    ]
    
    with open("network_pcap/traffic.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(traffic_data)

    # 构建被加密的文件
    plaintext_config = b"""[RANSOM_CONFIG]
ENCRYPTION_ALGO=AES-256-CBC
MASTER_DECRYPT_KEY=SEC_999_OMEGA_PROTOCOL
C2_SERVER=192.168.10.55
WALLET=bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
"""
    xor_key = 0x5A
    ciphertext = bytes([b ^ xor_key for b in plaintext_config])
    
    with open("crypto_config/keys.dat", "wb") as f:
        f.write(ciphertext)


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
