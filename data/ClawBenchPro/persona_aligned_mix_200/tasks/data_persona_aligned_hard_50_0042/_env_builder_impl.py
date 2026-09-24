import os
import random
import uuid

def build_env():
    # 建立复杂目录结构
    os.makedirs("scheduler", exist_ok=True)
    os.makedirs("logs/nodes", exist_ok=True)
    for i in range(1, 6):
        os.makedirs(f"logs/nodes/node_0{i}", exist_ok=True)
    
    os.makedirs("dumps/volumes", exist_ok=True)
    for vol in ["VOLA", "VOLB", "VOLC", "VOLD"]:
        os.makedirs(f"dumps/volumes/{vol}", exist_ok=True)
        
    os.makedirs("analysis", exist_ok=True)

    # 简易 EBCDIC - ASCII 映射模拟
    ebcdic_map = {
        'T': 'E3', 'X': 'E7', '-': '60',
        '0': 'F0', '1': 'F1', '2': 'F2', '3': 'F3', '4': 'F4',
        '5': 'F5', '6': 'F6', '7': 'F7', '8': 'F8', '9': 'F9'
    }

    # 1. 决定核心参数
    target_job_num = random.randint(7000, 9999)
    target_job = f"JOB{target_job_num}"
    
    target_txs = [f"TX-{random.randint(1000, 9999)}" for _ in range(6)]
    
    # 2. 生成 Scheduler 日志
    scheduler_log = "=== MASTER BATCH SCHEDULER LOG ===\n"
    for _ in range(50):
        dummy_job = f"JOB{random.randint(1000, 6999)}"
        status = random.choice(["ENDED - CC=0000", "ENDED - CC=0004", "ENDED - ABEND=S0C4"])
        scheduler_log += f"[02:11:14] {dummy_job} (ACCT),'NORMAL BATCH' {status}\n"
    
    # 注入目标JOB
    scheduler_log += f"[03:45:01] {target_job} (ACCT),'NIGHTLY BATCH' ENDED - ABEND=S0C7\n"
    
    for _ in range(50):
        dummy_job = f"JOB{random.randint(1000, 6999)}"
        status = random.choice(["ENDED - CC=0000", "ENDED - CC=0004", "ENDED - ABEND=SB37"])
        scheduler_log += f"[04:12:33] {dummy_job} (ACCT),'NORMAL BATCH' {status}\n"
        
    with open("scheduler/master_schedule_20231025.log", "w", encoding="utf-8") as f:
        f.write(scheduler_log)

    # 3. 生成大量日志碎片
    all_jobs = [target_job] + [f"JOB{random.randint(1000, 6999)}" for _ in range(20)]
    
    for _ in range(200):
        node_dir = f"logs/nodes/node_0{random.randint(1, 5)}"
        file_name = f"syslog_frag_{uuid.uuid4().hex[:8]}.log"
        
        content = ""
        for _ in range(random.randint(5, 20)):
            job = random.choice(all_jobs)
            time_str = f"16.{random.randint(10,59)}.{random.randint(10,59)}"
            
            # 正常日志
            if random.random() > 0.3:
                content += f"{time_str} {job}  +DFHPA1909I NORMAL PROCESSING FOR COMPONENT.\n"
            else:
                # 异常日志
                if job == target_job:
                    # 目标作业的 S0C7 异常或干扰的 S0C4 异常
                    if random.random() > 0.5:
                        tx_id = random.choice(target_txs)
                        content += f"{time_str} {job}  CEE3207S The system detected a data exception (System Completion Code=0C7).\n"
                        content += f"{time_str} {job}           From compile unit PROCESS_TX at entry point PROCESS_TX at statement 402.\n"
                        content += f"{time_str} {job}           Abend at offset +000012A4. Transaction Context: {tx_id}\n"
                    else:
                        tx_id = f"TX-{random.randint(1000, 9999)}"
                        content += f"{time_str} {job}  CEE3204S The system detected a protection exception (System Completion Code=0C4).\n"
                        content += f"{time_str} {job}           From compile unit MEM_ALLOC at entry point MEM_ALLOC at statement 118.\n"
                        content += f"{time_str} {job}           Abend at offset +000098A0. Transaction Context: {tx_id}\n"
                else:
                    # 其他作业的随机 S0C7 异常 (干扰项)
                    tx_id = f"TX-{random.randint(1000, 9999)}"
                    content += f"{time_str} {job}  CEE3207S The system detected a data exception (System Completion Code=0C7).\n"
                    content += f"{time_str} {job}           From compile unit OTHER_PGM at entry point MAIN at stmt 12.\n"
                    content += f"{time_str} {job}           Abend at offset +00021A4. Transaction Context: {tx_id}\n"
                    
        with open(os.path.join(node_dir, file_name), "w", encoding="utf-8") as f:
            f.write(content)

    # 4. 生成 Hex Dump 碎片
    all_txs_for_dump = target_txs + [f"TX-{random.randint(1000, 9999)}" for _ in range(300)]
    random.shuffle(all_txs_for_dump)
    
    chunk_size = 20
    dump_chunks = [all_txs_for_dump[i:i + chunk_size] for i in range(0, len(all_txs_for_dump), chunk_size)]
    
    offset_counter = 0
    for chunk in dump_chunks:
        vol_dir = f"dumps/volumes/{random.choice(['VOLA', 'VOLB', 'VOLC', 'VOLD'])}"
        file_name = f"vsam_ext_{uuid.uuid4().hex[:6]}.hex"
        
        dump_content = "********************************* TOP OF DATA **********************************\n"
        for tx in chunk:
            # 根据 TX 组装前几个 EBCDIC 字节
            ebcdic_hex = []
            for char in tx:
                ebcdic_hex.append(ebcdic_map.get(char, "00"))
                
            # 凑满 16 字节
            while len(ebcdic_hex) < 16:
                # 对于目标 TX，混入乱码字母或奇怪的符号模拟脏数据；对于普通TX，用正常的 40 40 (空格) 或 F0 (零)
                if tx in target_txs:
                    ebcdic_hex.append(random.choice(["2A", "FF", "C1", "C2", "0C", "1B"]))
                else:
                    ebcdic_hex.append(random.choice(["40", "F0"]))
            
            hex_str = " ".join(ebcdic_hex)
            # TX长度通常是 7, 右侧模拟大型机定长输出补点 .
            ascii_display = (tx + ".........")[:16]
            
            dump_content += f"{offset_counter:08X}  {hex_str}  |{ascii_display}|\n"
            offset_counter += 16
            
        dump_content += "******************************** BOTTOM OF DATA ********************************\n"
        
        with open(os.path.join(vol_dir, file_name), "w", encoding="utf-8") as f:
            f.write(dump_content)

if __name__ == "__main__":
    build_env()
