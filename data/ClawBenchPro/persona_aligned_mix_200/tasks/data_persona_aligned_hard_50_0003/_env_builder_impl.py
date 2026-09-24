import os
import random
import json
from datetime import datetime, timedelta

def build_env():
    # 建立复杂深邃的废土目录树
    directories = [
        "lab_notes/2022_archived",
        "lab_notes/recent_logs",
        "config/hardware",
        "config/reagents",
        "sequencing_data",
        "results"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    random.seed(8848)

    # ---------------------------------------------------------
    # 1. 制造线索链：试剂盒与接头序列 (Decoys & The Truth)
    # ---------------------------------------------------------
    
    # 混淆实验笔记
    for i in range(15):
        date_str = (datetime.now() - timedelta(days=100 - i)).strftime("%Y-%m-%d")
        with open(f"lab_notes/2022_archived/exp_log_{date_str}.txt", "w") as f:
            f.write(f"Date: {date_str}\nRun ID: MinION_Run_Archive_{i}\n")
            f.write(f"Kit used: {random.choice(['TruSeq_v1', 'Nextera_V2', 'ScriptSeq'])}\n")
            f.write("Status: Failed due to sensor overheat.\n")

    # 真实的实验笔记埋藏在 recent_logs 中
    with open("lab_notes/recent_logs/emergency_shift_03.md", "w") as f:
        f.write("# Shift Report - Sector 4\n")
        f.write("The previous runs (Beta and Gamma) used old adapters.\n")
        f.write("For the critical `MinION_Run_Alpha`, we have switched the supplier.\n")
        f.write("WARNING: All `MinION_Run_Alpha` data must be trimmed for the `Nextera_V3` kit adapter!\n")
        f.write("Check the centralized configs for the exact nucleotide sequence.\n")

    for i in range(5):
        with open(f"lab_notes/recent_logs/noise_report_{i}.md", "w") as f:
            f.write(f"Just some random lab notes {random.randint(1000, 9999)}.\n")

    # 试剂盒配置文件（充斥着大量无用试剂盒）
    adapters_db = {
        "TruSeq_v1": "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT",
        "TruSeq_v2": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC",
        "Nextera_V2": "CTGTCTCTTATACACATCTGACG",
        "Nextera_V3": "CTGTCTCTTATACACATCT",  # <--- 这是真正的 target adapter
        "ScriptSeq": "AGATCGGAAGAGCACACGTCT",
        "NEBNext": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC"
    }
    
    # 故意打碎写入不同的 JSON 和 YAML，让 Agent 去搜
    with open("config/reagents/adapters_legacy.json", "w") as f:
        json.dump({k: v for k, v in adapters_db.items() if "Nextera" not in k}, f, indent=2)

    with open("config/reagents/adapters_nextera_series.json", "w") as f:
        json.dump({k: v for k, v in adapters_db.items() if "Nextera" in k}, f, indent=2)

    # ---------------------------------------------------------
    # 2. 制造数据碎片与规模压制 (FASTQ Generation)
    # ---------------------------------------------------------
    
    runs = ["MinION_Run_Alpha", "MinION_Run_Beta", "MinION_Run_Gamma", "MinION_Run_Delta"]
    bases = ['A', 'T', 'C', 'G']
    target_adapter = adapters_db["Nextera_V3"]

    def gen_seq(length):
        return "".join(random.choices(bases, k=length))

    def gen_qual(length, target_mean_quality):
        # 围绕 target_mean_quality 生成 ascii 字符 (Phred 33)
        # 例如 target_mean=20 -> ascii 平均为 53
        quals = []
        for _ in range(length):
            # 允许有一定波动
            q = target_mean_quality + random.randint(-5, 5)
            q = max(0, min(40, q)) # phred 范围 0-40
            quals.append(chr(q + 33))
        return "".join(quals)

    read_counter = 0

    # 遍历不同的 Run 批次生成海量散落文件
    for run in runs:
        # 每个 Run 下有随机深度的车道和碎片目录
        for lane in range(1, 6):
            lane_path = f"sequencing_data/{run}/lane_{lane:02d}/chunks/deep_storage"
            os.makedirs(lane_path, exist_ok=True)
            
            # 每个目录下 5 到 10 个切片文件
            num_chunks = random.randint(5, 10)
            for chunk_idx in range(num_chunks):
                # 随机文件扩展名，有些是 fq, 有些是 fastq，甚至混有 log
                ext = random.choice([".fastq", ".fq", ".log.tmp"])
                filename = f"chunk_{random.randint(10000, 99999)}_{chunk_idx}{ext}"
                
                # 如果是 log.tmp 就直接写乱码跳过
                if ext == ".log.tmp":
                    with open(os.path.join(lane_path, filename), "w") as f:
                        f.write(f"CRITICAL ERROR 0x{random.randint(1000, 9999)}\nMEMORY DUMP CORRUPTED.\n")
                    continue
                
                # 写 FASTQ 数据
                with open(os.path.join(lane_path, filename), "w") as f:
                    # 每个切片 20~50 条 reads
                    num_reads = random.randint(20, 50)
                    for _ in range(num_reads):
                        read_counter += 1
                        read_id = f"@READ_{read_counter:07d}_run_{run}_lane{lane}"
                        
                        # 命运轮盘
                        # 1: 好数据 (均值>20, 无污染)
                        # 2: 质量差 (均值<20)
                        # 3: 有接头污染 (针对 target_adapter 或者是旧 adapter)
                        fate = random.choice(["good", "bad_quality", "contaminated", "borderline"])
                        
                        if fate == "good":
                            seq = gen_seq(100)
                            qual = gen_qual(100, 25) # 稳过 20
                        elif fate == "bad_quality":
                            seq = gen_seq(100)
                            qual = gen_qual(100, 15) # 稳不过 20
                        elif fate == "borderline":
                            # 极限测试: 平均恰好 19.5 (不过) 或者 20.1 (过)
                            is_pass = random.choice([True, False])
                            target_q = 20 if is_pass else 19
                            seq = gen_seq(100)
                            qual = gen_qual(100, target_q) 
                            # 精调确保严格跨界
                        else:
                            # 包含污染
                            seq_len = 100
                            adapter = target_adapter if run == "MinION_Run_Alpha" else adapters_db["TruSeq_v1"]
                            insert_pos = random.randint(10, seq_len - len(adapter) - 5)
                            prefix = gen_seq(insert_pos)
                            suffix = gen_seq(seq_len - insert_pos - len(adapter))
                            seq = prefix + adapter + suffix
                            qual = gen_qual(100, 28) # 质量好，但被污染

                        f.write(f"{read_id}\n{seq}\n+\n{qual}\n")

if __name__ == "__main__":
    build_env()
