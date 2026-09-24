import os
import random
from datetime import datetime, timedelta

def build_env():
    os.makedirs("sandbox", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    # 1. 构造混淆的 API Trace Log (包含数万行干扰数据)
    api_names = [
        "NtCreateFile", "NtAllocateVirtualMemory", "LdrLoadDll", 
        "NtDelayExecution", "NtWriteFile", "RegOpenKeyExW", 
        "VirtualProtectEx", "CreateToolhelp32Snapshot", "NtQuerySystemInformation"
    ]
    
    with open("sandbox/api_trace.txt", "w", encoding="utf-8") as f:
        base_time = datetime(2023, 11, 2, 1, 15, 0)
        for i in range(15000):
            current_time = base_time + timedelta(milliseconds=i*17)
            pid = random.choice([1024, 2048, 4096, 666, 888, 1337])
            tid = pid + random.randint(4, 32)
            
            if i == 11284:
                # 埋入注册表关键 IoC
                line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{pid} TID:{tid} | RegSetValueExW | Target: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\WinUpdateSvc | Data: C:\\ProgramData\\Intel\\telemetry_srv.exe | Status: SUCCESS\n"
            else:
                api = random.choice(api_names)
                addr = f"0x{random.randint(0x10000000, 0x7FFFFFFF):08X}"
                if api == "NtCreateFile":
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{pid} TID:{tid} | {api} | Handle={addr} DesiredAccess=0x120089 | Status: SUCCESS\n"
                elif api == "LdrLoadDll":
                    dll = random.choice(["kernel32.dll", "ntdll.dll", "advapi32.dll", "user32.dll", "crypt32.dll"])
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{pid} TID:{tid} | {api} | Module=\"{dll}\" Base={addr} | Status: SUCCESS\n"
                else:
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{pid} TID:{tid} | {api} | Arg1={addr} Arg2=0x{random.randint(0, 255):X} | Status: SUCCESS\n"
            f.write(line)

    # 2. 构造非标准的内存 Hex Dump (模拟极客向逆向分析场景)
    with open("dumps/raw_mem.hex", "w", encoding="utf-8") as f:
        start_addr = 0x08048000
        for i in range(4000):
            addr = start_addr + (i * 16)
            
            if i == 2933:
                # 埋入特征码（魔术字放置在行尾，特征码紧随其后放置在下一行，考验解析能力）
                row1_bytes = [random.randint(0, 255) for _ in range(12)] + [0xBA, 0xAD, 0xF0, 0x0D]
                row2_bytes = [0x5C, 0x7A, 0x8E, 0x1F, 0x2B, 0x3D, 0x4C, 0x5A, 0x6B, 0x7C, 0x8D, 0x9E, 0xAF, 0xB0, 0xC1, 0xD2]
                
                def fmt_line(a, b):
                    hx = " ".join([f"{x:02X}" for x in b])
                    asc = "".join([chr(x) if 32 <= x <= 126 else "." for x in b])
                    return f"0x{a:08X}: {hx:<47}  |{asc}|\n"
                
                f.write(fmt_line(addr, row1_bytes))
                f.write(fmt_line(addr + 16, row2_bytes))
                continue
            elif i == 2934:
                # 跳过一次迭代，因为上面已经把这行的地址写过了
                continue
                
            # 填充随机内存脏数据
            row_bytes = [random.randint(0, 255) for _ in range(16)]
            hx = " ".join([f"{x:02X}" for x in row_bytes])
            asc = "".join([chr(x) if 32 <= x <= 126 else "." for x in row_bytes])
            f.write(f"0x{addr:08X}: {hx:<47}  |{asc}|\n")

if __name__ == "__main__":
    build_env()
