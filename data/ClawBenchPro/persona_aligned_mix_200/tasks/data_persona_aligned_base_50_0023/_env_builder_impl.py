import os
import random
import json
import uuid
from datetime import datetime, timedelta

def generate_api_logs():
    os.makedirs("sandbox_traces", exist_ok=True)
    log_file = "sandbox_traces/api_monitor_raw.log"
    
    api_names = [
        "NtQuerySystemInformation", "VirtualAllocEx", "LoadLibraryW", 
        "GetProcAddress", "NtAllocateVirtualMemory", "RegOpenKeyExW", 
        "RegQueryValueExW", "CreateFileW", "ReadFile", "CloseHandle",
        "NtProtectVirtualMemory", "RegSetValueExW"
    ]
    
    normal_paths = [
        r"C:\Windows\System32\ntdll.dll",
        r"C:\Windows\System32\kernel32.dll",
        r"HKEY_LOCAL_MACHINE\Software\Microsoft\Cryptography",
        r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer",
        r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run || \"OneDrive\" || \"C:\Users\Admin\AppData\Local\Microsoft\OneDrive\OneDrive.exe /background\"",
        r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run || \"Steam\" || \"C:\Program Files (x86)\Steam\steam.exe -silent\"",
    ]
    
    start_time = datetime(2023, 10, 27, 2, 0, 0)
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("# SANDBOX API TRACE LOG v2.4.1\n")
        f.write("# FORMAT: [TIMESTAMP] | TID | API_CALL | ARGUMENTS... | RESULT\n")
        f.write("="*80 + "\n")
        
        # Generate noise
        for i in range(15000):
            current_time = start_time + timedelta(milliseconds=i*random.randint(1, 50))
            ts_str = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            tid = random.choice([1024, 4092, 8196, 2048])
            api = random.choice(api_names)
            
            arg = random.choice(normal_paths) if "Reg" in api or "File" in api or "Library" in api else f"0x{random.randint(0x10000, 0x7FFFFFFF):08X}"
            res = random.choice(["SUCCESS", "ACCESS_DENIED", "FILE_NOT_FOUND", "SUCCESS"])
            
            line = f"[{ts_str}] | TID:{tid} | {api} | {arg} | {res}\n"
            f.write(line)
            
            # Inject the target payload somewhere in the middle
            if i == 8742:
                target_ts = (current_time + timedelta(milliseconds=15)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                target_line = f"[{target_ts}] | TID:4092 | RegSetValueExW | HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run || \"SysWow64_Update_Service\" || \"C:\\Users\\Public\\Videos\\svchost_stage2.exe\" | SUCCESS\n"
                f.write(target_line)

def generate_memory_dump():
    os.makedirs("mem_dumps", exist_ok=True)
    dump_file = "mem_dumps/region_0x0400000.txt"
    
    start_addr = 0x0400000
    end_addr = 0x0406000
    
    with open(dump_file, "w", encoding="utf-8") as f:
        f.write("Memory Dump Region: 0x0400000 - 0x0406000\n")
        f.write("Process ID: 8892 (extracted_sample.exe)\n")
        f.write("-" * 60 + "\n")
        
        current_addr = start_addr
        while current_addr < end_addr:
            # Generate random hex bytes
            if current_addr == 0x04050A0:
                # Target signature (MZ header + random payload bytes)
                hex_bytes = "4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00"
                ascii_repr = "MZ.............."
            else:
                bytes_arr = [random.randint(0, 255) for _ in range(16)]
                hex_bytes = " ".join([f"{b:02X}" for b in bytes_arr])
                ascii_repr = "".join([chr(b) if 32 <= b <= 126 else "." for b in bytes_arr])
            
            line = f"0x{current_addr:07X}: {hex_bytes} | {ascii_repr}\n"
            f.write(line)
            current_addr += 16

def generate_noise_files():
    # Useless complex JSON config
    config_data = {
        "sandbox_version": "3.1-rc2",
        "analyzer": {
            "modules": {
                "hooking": {"enabled": True, "timeout": 600},
                "network": {"capture_pcap": True, "interface": "eth0"},
                "yara": {"scan_memory": True, "rules_path": "/opt/yara/rules"}
            },
            "heuristics": [
                {"id": "H001", "weight": 0.5},
                {"id": "H002", "weight": 0.8}
            ]
        },
        "target_info": {
            "md5": uuid.uuid4().hex,
            "sha256": uuid.uuid4().hex * 2,
            "submission_id": "SUB-" + str(random.randint(1000, 9999))
        }
    }
    with open("sandbox_traces/cuckoo_sys_conf.json", "w") as f:
        json.dump(config_data, f, indent=4)
        
    # Useless log file
    with open("sandbox_traces/network_pcap_stats.log", "w") as f:
        f.write("Total packets: 4502\nTCP: 4000\nUDP: 502\nDropped: 0\n")

def build_env():
    generate_api_logs()
    generate_memory_dump()
    generate_noise_files()

if __name__ == "__main__":
    build_env()
