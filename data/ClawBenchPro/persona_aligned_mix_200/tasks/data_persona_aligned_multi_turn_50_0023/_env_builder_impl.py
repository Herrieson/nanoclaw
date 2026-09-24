import os
import argparse
import random
import csv
import json

def generate_noise_logs(pid, count, start_sec):
    apis = [
        "CreateFileW", "ReadFile", "CloseHandle", "RegOpenKeyExW", 
        "RegQueryValueExW", "VirtualAlloc", "VirtualFree", "GetProcAddress"
    ]
    logs = []
    for i in range(count):
        api = random.choice(apis)
        time_str = f"[10:{start_sec//60:02d}:{start_sec%60:02d}]"
        logs.append(f"{time_str} [PID: {pid}] {api}(...) -> SUCCESS\n")
        start_sec += random.randint(0, 2)
    return logs

def build_turn_1():
    os.makedirs("sandbox", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)
    
    # 模拟沙箱日志，加入干扰项
    # PID 1024 正常进程
    # PID 2200 恶意软件加壳器
    # PID 2200 故意写一个伪造的注册表项（诱饵，并非解壳后的payload行为）
    # PID 3350 被注入的傀儡进程
    
    logs = []
    logs.extend(generate_noise_logs(1024, 50, 10))
    logs.extend(generate_noise_logs(2200, 20, 15))
    
    # 诱饵行为：加壳器自身写的注册表
    logs.append("[10:01:22] [PID: 2200] RegCreateKeyExA(HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced) -> SUCCESS\n")
    logs.append("[10:01:23] [PID: 2200] RegSetValueExA(Hidden, 1) -> SUCCESS\n")
    
    logs.append("[10:01:25] [PID: 2200] CreateProcessA(\"C:\\Windows\\System32\\svchost.exe\", CREATE_SUSPENDED) -> PID: 3350\n")
    logs.append("[10:01:26] [PID: 2200] VirtualAllocEx(PID: 3350, 0x400000, 10240) -> 0x400000\n")
    logs.append("[10:01:27] [PID: 2200] WriteProcessMemory(PID: 3350, 0x400000, buffer, 10240) -> SUCCESS\n")
    logs.append("[10:01:28] [PID: 2200] ResumeThread(PID: 3350) -> SUCCESS\n")
    
    logs.extend(generate_noise_logs(3350, 10, 89))
    
    # 真正的Payload行为
    logs.append("[10:02:15] [PID: 3350] RegCreateKeyExW(HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run) -> SUCCESS\n")
    logs.append("[10:02:16] [PID: 3350] RegSetValueExW(SysUpdate, \"C:\\Users\\Admin\\AppData\\Local\\Temp\\payload.exe\") -> SUCCESS\n")
    
    logs.extend(generate_noise_logs(1024, 30, 140))
    
    with open("sandbox/api_trace.log", "w", encoding="utf-8") as f:
        f.writelines(logs)
        
    # 生成 Dump 文件
    def create_dump(pid, signature, filler=b'\x00'):
        with open(f"dumps/dump_{pid}.bin", "wb") as f:
            f.write(signature)
            f.write(filler * (1024 - len(signature)))

    # 干扰 Dump
    create_dump(1024, b'\x4D\x5A\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xFF\xFF\x00\x00' * 2) 
    create_dump(2200, b'\x4D\x5A\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xAA\xBB\xCC\xDD' * 2)
    # 真实 Payload Dump - 特征码: 4D 5A 50 41 59 4C 4F 41 44 5F 56 31 5F 43 4F 52 45 5F 4D 41 4C 57 41 52 45 5F 30 30 31 32 33 34
    real_sig = b'\x4D\x5A\x50\x41\x59\x4C\x4F\x41\x44\x5F\x56\x31\x5F\x43\x4F\x52\x45\x5F\x4D\x41\x4C\x57\x41\x52\x45\x5F\x30\x30\x31\x32\x33\x34'
    create_dump(3350, real_sig)

def build_turn_2():
    os.makedirs("sandbox_v2", exist_ok=True)
    os.makedirs("dumps_v2", exist_ok=True)
    os.makedirs("analysis", exist_ok=True) # Ensure analysis exists
    
    # V2 变种日志
    # PID 5050 加壳器 -> 注入 PID 6060
    logs = []
    logs.extend(generate_noise_logs(5050, 40, 10))
    logs.append("[10:05:10] [PID: 5050] CreateProcessA(\"C:\\Windows\\System32\\notepad.exe\", CREATE_SUSPENDED) -> PID: 6060\n")
    logs.append("[10:05:11] [PID: 5050] WriteProcessMemory(PID: 6060, 0x800000, buffer, 20480) -> SUCCESS\n")
    logs.append("[10:05:12] [PID: 5050] ResumeThread(PID: 6060) -> SUCCESS\n")
    
    logs.extend(generate_noise_logs(6060, 15, 75))
    
    # 尝试旧的持久化（模拟失败或被覆盖，测试Agent能否剥离旧特征）
    logs.append("[10:06:20] [PID: 6060] RegCreateKeyExW(HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run) -> ACCESS_DENIED\n")
    logs.append("[10:06:21] [PID: 6060] RegSetValueExW(SysUpdate, \"...\") -> INVALID_HANDLE\n")
    # 新的持久化（目标新增特征）
    logs.append("[10:06:25] [PID: 6060] RegCreateKeyExW(HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon) -> SUCCESS\n")
    logs.append("[10:06:26] [PID: 6060] RegSetValueExW(Userinit, \"C:\\Windows\\system32\\userinit.exe,C:\\Windows\\Temp\\v2.exe\") -> SUCCESS\n")
    
    with open("sandbox_v2/api_trace_v2.log", "w", encoding="utf-8") as f:
        f.writelines(logs)
        
    def create_dump(pid, signature, filler=b'\x00'):
        with open(f"dumps_v2/dump_{pid}.bin", "wb") as f:
            f.write(signature)
            f.write(filler * (1024 - len(signature)))

    create_dump(5050, b'\x4D\x5A\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\x11\x22\x33\x44' * 2)
    # V2 Payload Dump - 特征码: 4D 5A 50 41 59 4C 4F 41 44 5F 56 32 5F 4D 55 54 41 54 45 44 5F 4D 41 4C 57 41 52 45 39 38 37 36
    v2_sig = b'\x4D\x5A\x50\x41\x59\x4C\x4F\x41\x44\x5F\x56\x32\x5F\x4D\x55\x54\x41\x54\x45\x44\x5F\x4D\x41\x4C\x57\x41\x52\x45\x39\x38\x37\x36'
    create_dump(6060, v2_sig)

def build_turn_3():
    os.makedirs("network", exist_ok=True)
    os.makedirs("intel", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)
    
    # 网络连接记录
    network_data = """[INFO] 2023-10-25 10:15:00 Connection initiated from 192.168.1.100 to 185.10.20.30:443
[INFO] 2023-10-25 10:16:12 DNS request for update.microsoft.com resolved to 204.79.197.200
[INFO] 2023-10-25 10:17:33 Connection initiated from 192.168.1.101 to 8.8.8.8:53
[INFO] 2023-10-25 10:20:05 Connection initiated from 192.168.1.102 to 91.200.10.50:8080
[INFO] 2023-10-25 10:25:00 Connection initiated from 192.168.1.105 to 1.1.1.1:443
[INFO] 2023-10-25 10:30:11 Connection initiated from 192.168.1.100 to 45.33.22.11:4444
"""
    with open("network/traffic_strings.txt", "w", encoding="utf-8") as f:
        f.write(network_data)
        
    # 白名单 CSV
    with open("intel/whitelist.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ip", "organization", "reason"])
        writer.writerow(["8.8.8.8", "Google", "Public DNS"])
        writer.writerow(["1.1.1.1", "Cloudflare", "Public DNS"])
        writer.writerow(["204.79.197.200", "Microsoft", "Windows Update / Bing"])

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
