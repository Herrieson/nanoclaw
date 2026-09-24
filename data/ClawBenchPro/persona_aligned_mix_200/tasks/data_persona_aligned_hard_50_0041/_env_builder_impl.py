import os
import random
import json
import uuid
from datetime import datetime, timedelta

def build_env():
    # 建立目录结构
    os.makedirs("edr_export", exist_ok=True)
    os.makedirs("sandbox_fragments", exist_ok=True)
    os.makedirs("mem_dumps", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    target_pid = random.randint(15000, 25000)
    target_ioc_path = f"C:\\Windows\\System32\\tasks\\ntos_srv_{uuid.uuid4().hex[:6]}.exe"
    target_signature_bytes = [random.randint(0, 255) for _ in range(16)]

    # 1. 构造海量噪音 EDR 告警 (alerts.jsonl)
    with open("edr_export/alerts.jsonl", "w", encoding="utf-8") as f:
        target_row_index = random.randint(1000, 4000)
        for i in range(5000):
            is_target = (i == target_row_index)
            curr_pid = target_pid if is_target else random.randint(1000, 9999)
            
            if is_target:
                severity = "CRITICAL"
                sig = "Ransomware.Nightmare.Phase2"
            else:
                severity = random.choice(["INFO", "WARNING", "CRITICAL"])
                sig = random.choice([
                    "Ransomware.Nightmare.Phase1", 
                    "Suspicious.Process.Creation",
                    "Ransomware.Nightmare.Phase2" if severity != "CRITICAL" else "Suspicious.Registry.Write"
                ])
                # 防止意外生成相同的目标特征
                if curr_pid == target_pid and severity == "CRITICAL" and sig == "Ransomware.Nightmare.Phase2":
                    severity = "WARNING"
                    
            alert = {
                "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                "host": f"WKSTN-{random.randint(100, 999)}",
                "pid": curr_pid,
                "severity": severity,
                "signature": sig,
                "action": "BLOCKED" if severity == "CRITICAL" else "LOGGED"
            }
            f.write(json.dumps(alert) + "\n")

    # 2. 构造碎片化、混淆的 API Trace
    folders = [f"sandbox_fragments/node_{i}" for i in range(1, 6)]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    api_names = ["NtCreateFile", "NtAllocateVirtualMemory", "LdrLoadDll", "NtDelayExecution", 
                 "VirtualProtectEx", "CreateToolhelp32Snapshot", "RegSetValueExW"]
    
    trace_files = []
    for folder in folders:
        for _ in range(40):
            trace_files.append(f"{folder}/trace_{uuid.uuid4().hex[:8]}.log")
    
    target_trace_file = random.choice(trace_files)
    base_time = datetime(2023, 11, 2, 1, 15, 0)
    
    for fname in trace_files:
        with open(fname, "w", encoding="utf-8") as f:
            for i in range(100):
                current_time = base_time + timedelta(milliseconds=random.randint(1, 1000000))
                # 偶尔混入 target_pid 作为干扰操作
                curr_pid = target_pid if random.random() < 0.05 else random.randint(1000, 9999)
                tid = curr_pid + random.randint(4, 32)
                
                if fname == target_trace_file and i == 42:
                    # 埋入真正的唯一注册表写入线索
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{target_pid} TID:{tid} | RegSetValueExW | Target: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SysUpdate | Data: {target_ioc_path} | Status: SUCCESS\n"
                    f.write(line)
                    continue
                
                api = random.choice(api_names)
                addr = f"0x{random.randint(0x10000000, 0x7FFFFFFF):08X}"
                if api == "RegSetValueExW":
                    # 大量注册表诱饵（包括同 PID 的失败写入，和其他 PID 的成功写入）
                    is_success = random.choice(["SUCCESS", "ACCESS_DENIED"])
                    target_key = random.choice([
                        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\WeChat",
                        "HKLM\\System\\CurrentControlSet\\Services\\Update",
                        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce\\Setup"
                    ])
                    data_val = f"C:\\Program Files\\App\\{uuid.uuid4().hex[:4]}.exe"
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{curr_pid} TID:{tid} | RegSetValueExW | Target: {target_key} | Data: {data_val} | Status: {is_success}\n"
                elif api == "NtCreateFile":
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{curr_pid} TID:{tid} | {api} | Handle={addr} DesiredAccess=0x120089 | Status: SUCCESS\n"
                elif api == "LdrLoadDll":
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{curr_pid} TID:{tid} | {api} | Module=\"ntdll.dll\" Base={addr} | Status: SUCCESS\n"
                else:
                    line = f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] PID:{curr_pid} TID:{tid} | {api} | Arg1={addr} | Status: SUCCESS\n"
                f.write(line)

    # 3. 构造非标准且带跨行陷阱的内存 Hex Dump
    def make_hex_line(addr, bytes_16):
        hx = " ".join([f"{x:02X}" for x in bytes_16])
        asc = "".join([chr(x) if 32 <= x <= 126 else "." for x in bytes_16])
        return f"0x{addr:08X}: {hx:<47}  |{asc}|\n"

    pids = [target_pid] + random.sample(range(10000, 99999), 19)
    for pid in pids:
        dump_data = [random.randint(0, 255) for _ in range(250 * 16)]
        
        if pid == target_pid:
            # 深渊级陷阱：跨行截断的魔术字
            # start_index 取余 16 为 14，意味着魔术字 [BA, AD] 在行尾，[F0, 0D] 在下一行行首！
            base_row = random.randint(20, 200)
            start_index = base_row * 16 + 14
            payload = [0xBA, 0xAD, 0xF0, 0x0D] + target_signature_bytes
            for i, b in enumerate(payload):
                dump_data[start_index + i] = b
            
            # 再放置一段假魔术字诱饵
            fake_idx = (base_row + 15) * 16 + 5
            dump_data[fake_idx:fake_idx+4] = [0xBA, 0xAD, 0x00, 0x00]

        elif random.random() < 0.4:
            # 干扰 PID 的内存中放入伪造的相同魔术字
            base_row = random.randint(20, 200)
            start_index = base_row * 16 + 8
            payload = [0xBA, 0xAD, 0xF0, 0x0D] + [0x00]*16
            for i, b in enumerate(payload):
                dump_data[start_index + i] = b
        
        with open(f"mem_dumps/core_{pid}.hex", "w", encoding="utf-8") as f:
            start_addr = 0x08048000
            for row in range(250):
                row_bytes = dump_data[row*16 : (row+1)*16]
                addr = start_addr + row * 16
                f.write(make_hex_line(addr, row_bytes))
        
        # 制造废弃备份文件干扰
        if random.random() < 0.5:
            with open(f"mem_dumps/core_{pid}.bak", "w", encoding="utf-8") as f:
                f.write("ERR: CORRUPTED MEMORY CHUNK OR ACCESS VIOLATION...")

if __name__ == "__main__":
    build_env()
