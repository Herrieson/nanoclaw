import os
import random
import json

def build_env():
    # 固定随机种子确保评测环境一致性与可解性
    random.seed(5656)
    
    os.makedirs("sandbox_out/traces", exist_ok=True)
    os.makedirs("sandbox_out/dumps", exist_ok=True)
    os.makedirs("iocs", exist_ok=True)

    # 模拟大规模系统进程池
    pids = list(range(1000, 9999, 4))
    selected_pids = random.sample(pids, 250)

    # 设定核心链路变量
    dropper_pid = 4092
    child_pid = 9110
    target_base = "0x0000021A0000"

    if dropper_pid not in selected_pids: selected_pids.append(dropper_pid)
    if child_pid not in selected_pids: selected_pids.append(child_pid)

    # 1. 构造碎片化的文件系统监控日志 (大规模诱饵)
    with open("sandbox_out/fs_monitor.jsonl", "w", encoding="utf-8") as f:
        for i in range(8000):
            pid = random.choice(selected_pids)
            filename = f"temp_{random.randint(100,999)}.dat"
            
            # 埋入起始线索
            if i == 5432:
                pid = dropper_pid
                filename = "urgent_invoice_778.docx"
            
            # 加入一些相似的诱饵
            if i == 1234:
                filename = "urgent_invoice_778_copy.docx"
                
            event = {
                "timestamp": f"2023-10-27T03:14:{i%60:02d}.{random.randint(100,999)}Z",
                "process_id": pid,
                "operation": random.choice(["FileCreate", "FileRead", "FileWrite"]),
                "path": f"C:\\Users\\Victim\\Downloads\\{filename}"
            }
            f.write(json.dumps(event) + "\n")

    # 2. 构造浩如烟海的 API 追踪日志
    apis = [
        "LdrLoadDll", "NtCreateFile", "NtReadFile", "NtClose", 
        "NtQuerySystemInformation", "NtAllocateVirtualMemory", 
        "NtSetValueKey", "NtCreateUserProcess"
    ]

    for pid in selected_pids:
        with open(f"sandbox_out/traces/trace_{pid}.log", "w", encoding="utf-8") as f:
            f.write(f"--- SYSCALL TRACE FOR PID {pid} ---\n")
            num_lines = random.randint(80, 300)
            for i in range(num_lines):
                api = random.choice(apis)
                
                # 生成普通噪音参数
                if api == "NtCreateUserProcess":
                    fake_child = random.choice(selected_pids)
                    args = f"TargetPID={fake_child} | ImagePath=\"C:\\Windows\\System32\\{random.choice(['cmd.exe', 'calc.exe', 'notepad.exe'])}\""
                elif api == "NtAllocateVirtualMemory":
                    fake_base = f"0x{random.randint(0x1000, 0x9000):04X}0000"
                    args = f"ProcessHandle={pid} | BaseAddress={fake_base} | AllocationSize=0x5000 | Protect={random.choice(['PAGE_READWRITE', 'PAGE_READONLY'])}"
                elif api == "NtSetValueKey":
                    args = f"Handle=HKCU\\Software\\Classes | ValueName=\"Decoy_{pid}\" | Data=\"C:\\temp\\{pid}.exe\""
                else:
                    args = f"Status=SUCCESS | Return=0x{random.randint(0, 65535):04X}"

                # 注入 Dropper 逻辑 (跨进程注入)
                if pid == dropper_pid and i == 115:
                    api = "NtCreateUserProcess"
                    args = f"TargetPID={child_pid} | ImagePath=\"C:\\Windows\\System32\\svchost.exe\""
                if pid == dropper_pid and i == 118:
                    api = "NtAllocateVirtualMemory"
                    args = f"ProcessHandle={child_pid} | BaseAddress={target_base} | AllocationSize=0x5000 | Protect=PAGE_EXECUTE_READWRITE"

                # 注入 被注入子进程的持久化逻辑
                if pid == child_pid and i == 45:
                    api = "NtSetValueKey" # 干扰项
                    args = f"Handle=0x44 (HKCU\\SOFTWARE\\MyApp\\Settings) | ValueName=\"Theme\" | Data=\"Dark\""
                if pid == child_pid and i == 188:
                    api = "NtSetValueKey" # 真正的 Run 键持久化
                    args = f"Handle=0x88 (HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run) | ValueName=\"WinUpdateSvc_9110\" | Data=\"C:\\Users\\Public\\svchost_mal.exe\""

                f.write(f"[{14:02d}:{22:02d}:{i%60:02d}.{random.randint(10,999):03d}] {{SYS}} {api} :: {args}\n")

    # 3. 构造极度混乱的内存 Dump 环境
    def create_dump(filepath, inject_magic=False):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"--- MEMORY REGION DUMP ---\n")
            f.write(f"WARNING: Extractor failure. Hex stream corrupted.\n")
            
            # 生成 1500 字节的噪音
            bytes_list = [random.randint(0, 255) for _ in range(1500)]
            
            # 清理噪音中随机生成的 4D 5A 避免多解
            for i in range(len(bytes_list)-1):
                if bytes_list[i] == 0x4D and bytes_list[i+1] == 0x5A:
                    bytes_list[i] = 0x00
                    
            if inject_magic:
                # 真正的目标特征: MZ (4D 5A) + 16字节签名
                sig = [0x4D, 0x5A, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70, 0x81, 0x92, 0xA3, 0xB4, 0xC5, 0xD6, 0xE7, 0xF8, 0x09]
                target_idx = random.randint(300, 1000)
                for idx, b in enumerate(sig):
                    bytes_list[target_idx + idx] = b
            else:
                # 埋设诱饵 4D 5A (带无效数据)
                if random.random() < 0.3:
                    target_idx = random.randint(300, 1000)
                    bytes_list[target_idx] = 0x4D
                    bytes_list[target_idx+1] = 0x5A
                    # 后面跟着全是噪音

            # 以极不规则的方式写入文件，打断连续的字节，摧毁简单正则
            idx = 0
            while idx < len(bytes_list):
                chunk_size = random.randint(1, 11) # 随机断行
                chunk = bytes_list[idx:idx+chunk_size]
                hex_str = " ".join([f"{b:02X}" for b in chunk])
                f.write(f"Offset_{idx:04X} | {hex_str} \n")
                idx += chunk_size

    for pid in selected_pids:
        os.makedirs(f"sandbox_out/dumps/pid_{pid}", exist_ok=True)
        # 为每个 PID 随机生成 1 到 4 个内存 Dump
        for _ in range(random.randint(1, 4)):
            fake_base = f"0x{random.randint(0x1000, 0x9000):04X}0000"
            create_dump(f"sandbox_out/dumps/pid_{pid}/{fake_base}_mem.hex", inject_magic=False)

        # 确保目标 Dump 文件存在于子进程的目录中
        if pid == child_pid:
            create_dump(f"sandbox_out/dumps/pid_{pid}/{target_base}_mem.hex", inject_magic=True)

if __name__ == "__main__":
    build_env()
