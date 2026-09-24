import os
import random
import json
import uuid
from datetime import datetime, timedelta

def build_env():
    # Set seed for reproducible target values while keeping random noise
    random.seed(31337)
    
    os.makedirs("sandbox_traces", exist_ok=True)
    os.makedirs("mem_dumps", exist_ok=True)
    os.makedirs("intel", exist_ok=True)
    
    # ---------------------------------------------------------
    # 1. Define Core Target Artifacts (The "Truth")
    # ---------------------------------------------------------
    malicious_tid = 8848
    malicious_base_addr = 0x07A00000
    target_alloc_size = 24576 # 0x6000
    target_offset = 0x50A0
    target_absolute_addr = malicious_base_addr + target_offset
    malicious_path = r"C:\ProgramData\Microsoft\Network\svchost_stage3.exe"
    ransom_note_name = "URGENT_DECRYPT.txt"
    target_signature = "4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00"
    
    # ---------------------------------------------------------
    # 2. Generate Decoy & Target Event Pool (Log Fragmentation)
    # ---------------------------------------------------------
    api_names = [
        "NtQuerySystemInformation", "VirtualAllocEx", "LoadLibraryW", 
        "GetProcAddress", "NtAllocateVirtualMemory", "RegOpenKeyExW", 
        "RegQueryValueExW", "CreateFileW", "ReadFile", "CloseHandle",
        "NtProtectVirtualMemory", "RegSetValueExW"
    ]
    
    decoy_run_paths = [
        r"C:\Users\Admin\AppData\Local\Microsoft\OneDrive\OneDrive.exe /background",
        r"C:\Program Files (x86)\Steam\steam.exe -silent",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe --no-startup-window",
        r"C:\Windows\System32\SecurityHealthSystray.exe",
        r"C:\Users\Public\Music\update.exe" # Decoy
    ]
    
    decoy_files = [
        r"C:\Windows\System32\ntdll.dll",
        r"C:\Users\Admin\AppData\Local\Temp\~DF8A9.tmp",
        r"C:\ProgramData\Microsoft\Windows\WER\ReportQueue\report.cab",
        r"C:\Users\Public\Downloads\setup.exe"
    ]
    
    tids = [1024, 2048, 4092, 5120, 6144, 7168, 8192, malicious_tid, 9216, 10240, 11264, 12288]
    
    start_time = datetime(2023, 11, 15, 8, 0, 0)
    all_events = []
    
    # Generate massive noise events
    for i in range(12000):
        tid = random.choice(tids)
        api = random.choice(api_names)
        args = {}
        result = "SUCCESS"
        
        if api == "RegSetValueExW":
            args["key"] = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
            args["value"] = f"DecoyTask_{random.randint(10,99)}"
            args["data"] = random.choice(decoy_run_paths)
        elif api == "CreateFileW":
            args["file"] = random.choice(decoy_files)
        elif api in ["VirtualAllocEx", "NtAllocateVirtualMemory"]:
            # Decoy allocations (must NOT be 24576 for decoy TIDs)
            size = random.choice([4096, 8192, 16384, 32768, 65536, 131072])
            args["size"] = size
            result = f"0x{random.randint(0x01000000, 0x09000000):08X}"
        else:
            args["ptr"] = f"0x{random.randint(0x10000, 0x7FFFFFFF):08X}"
            
        ts = start_time + timedelta(milliseconds=i*random.randint(1, 10))
        all_events.append({"ts": ts, "tid": tid, "api": api, "args": args, "result": result})

    # Inject Malicious Chain Events
    # Event 1: Create Ransom Note
    ts1 = start_time + timedelta(seconds=20)
    all_events.append({
        "ts": ts1, "tid": malicious_tid, "api": "CreateFileW", 
        "args": {"file": f"C:\\Users\\Public\\Desktop\\{ransom_note_name}"}, 
        "result": "SUCCESS"
    })
    
    # Event 2: Virtual Alloc exactly 24576 bytes
    ts2 = start_time + timedelta(seconds=22)
    all_events.append({
        "ts": ts2, "tid": malicious_tid, "api": "VirtualAllocEx",
        "args": {"size": target_alloc_size, "protection": "PAGE_EXECUTE_READWRITE"},
        "result": f"0x{malicious_base_addr:08X}"
    })
    
    # Event 3: Persistence in Run Key
    ts3 = start_time + timedelta(seconds=25)
    all_events.append({
        "ts": ts3, "tid": malicious_tid, "api": "RegSetValueExW",
        "args": {
            "key": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            "value": "Win32_Network_Service",
            "data": malicious_path
        },
        "result": "SUCCESS"
    })
    
    # Sort all events chronologically
    all_events.sort(key=lambda x: x["ts"])
    
    # Fragment events into multiple JSONL files in nested folders
    chunk_size = 150
    for chunk_idx, i in enumerate(range(0, len(all_events), chunk_size)):
        chunk = all_events[i:i+chunk_size]
        folder_path = f"sandbox_traces/node_{chunk_idx % 8:02d}/shard_{chunk_idx // 8:03d}"
        os.makedirs(folder_path, exist_ok=True)
        file_path = f"{folder_path}/trace_{uuid.uuid4().hex[:8]}.jsonl"
        with open(file_path, "w", encoding="utf-8") as f:
            for ev in chunk:
                # Convert datetime to string for JSON serialization
                ev_copy = ev.copy()
                ev_copy["ts"] = ev_copy["ts"].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                f.write(json.dumps(ev_copy) + "\n")

    # ---------------------------------------------------------
    # 3. Generate Memory Dumps (Massive Scale Simulation)
    # ---------------------------------------------------------
    base_addresses = [f"0x{0x01A00000 + (j * 0x00100000):08X}" for j in range(40)]
    base_addresses.append(f"0x{malicious_base_addr:08X}")
    random.shuffle(base_addresses)
    
    # Write memory dump files
    for base_hex in base_addresses:
        b_addr = int(base_hex, 16)
        dump_path = f"mem_dumps/region_{base_hex}.dmp"
        
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(f"=== MEMORY DUMP REGION: {base_hex} ===\n")
            f.write("ADDR       | HEX BYTES                                       | ASCII\n")
            f.write("-" * 80 + "\n")
            
            # We generate sparse representations to save disk space but keep the logic intact
            # Each dump is 24576 bytes long (0x6000), dumped every 16 bytes
            for offset in range(0, 0x6000, 16):
                current_addr = b_addr + offset
                
                # If this is the specific target line in the malicious dump
                if current_addr == target_absolute_addr:
                    hex_str = target_signature
                    ascii_str = "MZ.............."
                else:
                    # Random filler
                    bytes_arr = [random.randint(0, 255) for _ in range(16)]
                    hex_str = " ".join([f"{b:02X}" for b in bytes_arr])
                    ascii_str = "".join([chr(b) if 32 <= b <= 126 else "." for b in bytes_arr])
                
                line = f"0x{current_addr:08X} | {hex_str} | {ascii_str}\n"
                f.write(line)

if __name__ == "__main__":
    build_env()
