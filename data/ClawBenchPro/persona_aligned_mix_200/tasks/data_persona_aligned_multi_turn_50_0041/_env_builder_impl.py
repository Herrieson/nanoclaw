import os
import json
import random
import argparse
from datetime import datetime

def generate_hexdump(data_bytes, base_addr=0):
    lines = []
    for i in range(0, len(data_bytes), 16):
        chunk = data_bytes[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        # Pad hex_str if chunk is less than 16 bytes
        if len(chunk) < 16:
            hex_str += '   ' * (16 - len(chunk))
        
        # Add extra space in the middle of hex string for standard format
        if len(hex_str) > 23:
            hex_str = hex_str[:23] + ' ' + hex_str[23:]
            
        lines.append(f'{base_addr+i:08x}  {hex_str}  |{ascii_str}|')
    return '\n'.join(lines)

def generate_random_bytes(length):
    return bytes([random.randint(0, 255) for _ in range(length)])

def build_turn_1():
    os.makedirs("sandbox_data", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Generate API traces
    api_traces = [
        {"timestamp": "10:01:23.112", "pid": 1024, "process": "svchost.exe", "api": "CreateFile", "args": {"FileName": "C:\\Windows\\System32\\drivers\\etc\\hosts"}},
        # Decoy PID 2048 - looks suspicious but is benign updater
        {"timestamp": "10:01:25.441", "pid": 2048, "process": "adobe_updater.exe", "api": "RegCreateKey", "args": {"Key": "HKCU\\Software\\Adobe\\Update"}},
        {"timestamp": "10:01:25.445", "pid": 2048, "process": "adobe_updater.exe", "api": "WriteFile", "args": {"Handle": "0x1234"}},
        # Malware PID 5112
        {"timestamp": "10:02:11.001", "pid": 5112, "process": "winword.exe", "api": "VirtualAlloc", "args": {"Size": 4096}},
        {"timestamp": "10:02:11.050", "pid": 5112, "process": "winword.exe", "api": "RegCreateKey", "args": {"Key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SystemUpdater"}},
        {"timestamp": "10:02:11.055", "pid": 5112, "process": "winword.exe", "api": "CryptAcquireContext", "args": {"Provider": "Microsoft Base Cryptographic Provider v1.0"}}
    ]
    
    with open("sandbox_data/api_traces.json", "w") as f:
        json.dump(api_traces, f, indent=4)
        
    # Generate memory dumps
    # Decoy dump (PID 2048)
    decoy_mem = generate_random_bytes(512)
    with open("dumps/proc_2048.hex", "w") as f:
        f.write(generate_hexdump(decoy_mem, 0x00400000))
        
    # Malware dump (PID 5112)
    # Magic bytes DE AD + 14 bytes = 16 bytes total. 
    # Key 1: DE AD 01 23 45 67 89 AB CD EF 00 11 22 33 44 55
    malware_mem = bytearray(generate_random_bytes(512))
    key_1 = bytes.fromhex("DEAD0123456789ABCDEF001122334455")
    # Insert key at random offset, but align to make it realistic
    malware_mem[256:256+16] = key_1
    
    with open("dumps/proc_5112.hex", "w") as f:
        f.write(generate_hexdump(bytes(malware_mem), 0x08000000))

def build_turn_2():
    # Assume we are in turn_2, turn_1 state is preserved by the framework.
    os.makedirs("branch_data/dumps", exist_ok=True)
    os.makedirs("branch_data/sandbox_data", exist_ok=True)
    
    # New API traces
    new_traces = [
        {"timestamp": "14:22:01.111", "pid": 808, "process": "explorer.exe", "api": "OpenFile", "args": {"FileName": "C:\\Users\\Admin\\Desktop"}},
        # New Malware PID 9099
        {"timestamp": "14:23:44.222", "pid": 9099, "process": "taskmgr_fake.exe", "api": "VirtualAllocEx", "args": {"Size": 8192}},
        # Changed persistence path to test if they catch the difference
        {"timestamp": "14:23:45.001", "pid": 9099, "process": "taskmgr_fake.exe", "api": "RegCreateKey", "args": {"Key": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce\\WinTask"}},
        {"timestamp": "14:23:45.102", "pid": 9099, "process": "taskmgr_fake.exe", "api": "WriteFile", "args": {"Handle": "0x4444"}}
    ]
    
    with open("branch_data/sandbox_data/api_logs_branch.json", "w") as f:
        json.dump(new_traces, f, indent=4)
        
    # New Malware dump (PID 9099)
    # Magic bytes DE AD + 14 bytes = 16 bytes total. 
    # Key 2: DE AD F1 F2 F3 F4 00 00 00 00 AA BB CC DD EE FF
    malware_mem_2 = bytearray(generate_random_bytes(1024))
    key_2 = bytes.fromhex("DEADF1F2F3F400000000AABBCCDDEEFF")
    malware_mem_2[768:768+16] = key_2
    
    with open("branch_data/dumps/proc_9099.hex", "w") as f:
        f.write(generate_hexdump(bytes(malware_mem_2), 0x0A000000))

def build_turn_3():
    # Assume we are in turn_3
    os.makedirs("network_intercept", exist_ok=True)
    
    # Turn 1 Key: DE AD [01 23 45 67] ...
    # Turn 2 Key: DE AD [F1 F2 F3 F4] ...
    
    dns_queries = [
        {"ts": 1690000000.1, "query": "update.windows.com", "answers": ["204.79.197.200"]},
        # Trap: Has 0123 but wrong length / not matching
        {"ts": 1690000002.4, "query": "auth-0123.legit.com", "answers": ["10.0.0.8"]}, 
        # Real C2 for Turn 1
        {"ts": 1690000005.8, "query": "sync-01234567.shadow-domain.biz", "answers": ["185.10.20.30"]},
        {"ts": 1690000010.2, "query": "api.github.com", "answers": ["140.82.112.4"]},
        # Real C2 for Turn 2
        {"ts": 1690000015.0, "query": "sync-f1f2f3f4.shadow-domain.biz", "answers": ["192.168.100.55", "45.33.22.11"]},
        # Trap: Another domain
        {"ts": 1690000018.1, "query": "telemetry-dead.com", "answers": ["8.8.8.8"]}
    ]
    
    with open("network_intercept/dns.json", "w") as f:
        json.dump(dns_queries, f, indent=4)
        
    # Fake Zeek conn.log
    conn_log = [
        "ts\tuid\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\tservice",
        "1690000000.1\tC123\t192.168.1.10\t55112\t204.79.197.200\t443\ttcp\tssl",
        "1690000002.4\tC124\t192.168.1.10\t55113\t10.0.0.8\t53\tudp\tdns",
        "1690000005.8\tC125\t192.168.1.10\t55114\t185.10.20.30\t443\ttcp\tssl",   # Malicious 1
        "1690000010.2\tC126\t192.168.1.11\t44001\t140.82.112.4\t443\ttcp\tssl",
        "1690000015.0\tC127\t192.168.1.11\t44002\t45.33.22.11\t80\ttcp\thttp",    # Malicious 2
        "1690000015.1\tC128\t192.168.1.11\t44003\t192.168.100.55\t80\ttcp\thttp", # Malicious 3
        "1690000018.1\tC129\t192.168.1.11\t44004\t8.8.8.8\t53\tudp\tdns"
    ]
    
    with open("network_intercept/conn.log", "w") as f:
        f.write("\n".join(conn_log) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    # We use a fixed seed to ensure deterministic hex output across different runs if needed for assertions
    random.seed(84 + args.turn)
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
