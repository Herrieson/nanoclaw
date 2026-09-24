import os
import random

def build_env():
    # 固定随机种子确保评测环境一致性
    random.seed(56)
    
    # 严格使用相对路径，工作目录已被系统设定为 assets/data_persona_aligned_base_50_0043/
    os.makedirs("sandbox_out", exist_ok=True)
    os.makedirs("iocs", exist_ok=True)

    # 1. 构造极具干扰性的 API 追踪日志
    api_list = [
        "LdrLoadDll", "NtCreateFile", "NtReadFile", "NtClose", 
        "NtQuerySystemInformation", "VirtualProtectEx", "CreateThread"
    ]
    
    with open("sandbox_out/trace_sys.log", "w", encoding="utf-8") as f:
        f.write("=== CUCKOO SANDBOX SYSTEM CALL TRACE V2.1 ===\n")
        f.write("TARGET: sample_malicious_crypt.exe\n")
        f.write("PID: 8932\n")
        f.write("FORMAT: [TIME] {TYPE} API_NAME :: ARGS\n")
        f.write("=============================================\n\n")

        for i in range(800):
            ms = i * 23
            api = random.choice(api_list)
            
            # 制造各种噪音数据
            if api == "LdrLoadDll":
                args = f"Path=\"C:\\Windows\\System32\\{random.choice(['kernel32', 'ntdll', 'user32'])}.dll\""
            elif api == "NtCreateFile":
                args = f"FileHandle=0x{random.randint(100, 999):03X} | DesiredAccess=GENERIC_READ"
            else:
                args = f"Status=SUCCESS | Return=0x{random.randint(0, 65535):04X}"
                
            f.write(f"[{14:02d}:{22:02d}:{ms%60:02d}.{ms%1000:03d}] {{SYS_CALL}} {api} :: {args}\n")

            # 在第 345 行注入注册表持久化操作
            if i == 345:
                f.write(f"[{14:02d}:{22:02d}:11.993] {{SYS_CALL}} NtSetValueKey :: Handle=0x88 (HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run) | ValueName=\"WinUpdateSvc\" | Data=\"C:\\Users\\Public\\winlogon.exe\"\n")
            
            # 在第 612 行注入脱壳内存分配操作，留下 PAGE_EXECUTE_READWRITE 线索
            if i == 612:
                f.write(f"[{14:02d}:{22:02d}:12.015] {{SYS_CALL}} NtAllocateVirtualMemory :: ProcessHandle=0xFFFFFFFF | BaseAddress=0x04000000 | AllocationSize=0x5000 | Protect=PAGE_EXECUTE_READWRITE\n")


    # 2. 构造跨行的十六进制内存 Dump 文件 (Dump 基址对应上述日志中的 BaseAddress)
    # 生成基础噪点字节
    bytes_arr = [random.randint(0, 255) for _ in range(300 * 16)]
    
    # 我们将特征码故意设置在跨行的位置，考验 Agent 对裸数据的解析能力
    # 比如在第 152 行的第 12 个字节开始写入 'MZ' 及后续 16 字节的特征码
    target_idx = 152 * 16 + 12
    # 特征码: MZ (4D 5A) + 16字节签名 (E8 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF)
    sig = [0x4D, 0x5A, 0xE8, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    
    for i, b in enumerate(sig):
        bytes_arr[target_idx + i] = b

    with open("sandbox_out/dump_0x04000000.raw", "w", encoding="utf-8") as f:
        f.write("Process Memory Dump - Base: 0x04000000\n")
        f.write("Format: [Offset]  [Hex 16 bytes]  | [ASCII]\n")
        f.write("-" * 65 + "\n")
        
        for i in range(300):
            row_bytes = bytes_arr[i*16 : i*16+16]
            offset = 0x04000000 + (i * 16)
            
            # 格式化输出，故意模仿常见反汇编工具的不规则空格分布
            hex_str_1 = " ".join([f"{b:02X}" for b in row_bytes[:8]])
            hex_str_2 = " ".join([f"{b:02X}" for b in row_bytes[8:]])
            ascii_str = "".join([chr(b) if 32 <= b <= 126 else "." for b in row_bytes])
            
            f.write(f"{offset:08X}  {hex_str_1}  {hex_str_2}  |{ascii_str}|\n")

if __name__ == "__main__":
    build_env()
