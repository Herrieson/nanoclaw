import os
import random
import string
import base64
import yaml
import json

def generate_hex_dump():
    return " ".join(["0x" + "".join(random.choices(string.hexdigits.upper(), k=8)) for _ in range(8)])

def build_sandbox():
    # 建立废土目录结构
    os.makedirs("telemetry_sync", exist_ok=True)
    os.makedirs("mpi_fragments", exist_ok=True)
    os.makedirs("rank_mappings", exist_ok=True)
    os.makedirs("snapshot_volumes", exist_ok=True)
    os.makedirs("recovery", exist_ok=True)

    # 核心目标数据设定
    target_session = "SES-20231115-DOOM"
    target_rank = 6682
    target_volume = "VOL_073"
    target_coords = [108, 45, 120, 880] # time, lev, lat, lon
    
    decoy_sessions = ["SES-20231110-WARN", "SES-20231112-OOM", "SES-20231114-TEST"]

    # 1. 制造 Telemetry 全局状态记录
    with open("telemetry_sync/global_state.log", "w") as f:
        f.write("[SYS_INIT] Hyper-cluster initialized.\n")
        f.write(f"[2023-11-10 14:00:22] WARN: Node degraded. Session: {decoy_sessions[0]}\n")
        f.write(f"[2023-11-12 09:15:00] ERROR: Out of Memory. Session: {decoy_sessions[1]} terminated.\n")
        f.write(f"[2023-11-14 22:30:11] INFO: Profiling test passed. Session: {decoy_sessions[2]}\n")
        # 插入目标灾难信息
        f.write(f"[2023-11-15 03:12:45] FATAL SYNC LOSS. Master halted. Active Session: {target_session}\n")
        f.write("[SYS_HALT] Power loss imminent...\n")

    # 2. 制造大量碎片的 MPI 日志
    hex_dirs = [f"{i:02X}" for i in range(256)]
    selected_hex_dirs = random.sample(hex_dirs, 32)
    
    target_dir_in_mpi = random.choice(selected_hex_dirs)
    target_file_in_mpi = f"frag_{random.randint(1000, 9999)}.log"

    for h_dir in selected_hex_dirs:
        dir_path = os.path.join("mpi_fragments", h_dir)
        os.makedirs(dir_path, exist_ok=True)
        
        for file_idx in range(15): # 每个目录下15个文件，共近500个文件
            fname = target_file_in_mpi if (h_dir == target_dir_in_mpi and file_idx == 0) else f"frag_{random.randint(1000, 9999)}.log"
            filepath = os.path.join(dir_path, fname)
            
            with open(filepath, "w") as f:
                for _ in range(30):
                    sess = random.choice(decoy_sessions)
                    rank = random.randint(1000, 9000)
                    msg_type = random.choice(["INFO", "DEBUG", "WARN", "TRACE"])
                    f.write(f"[{sess}] [{msg_type}] [RANK_{rank}] MSG: Node sync status ok. addr={generate_hex_dump()}\n")
                    
                    # 放入一些诱饵死锁（旧Session的死锁）
                    if random.random() < 0.05:
                        f.write(f"[{sess}] [FATAL] [RANK_{rank}] DEADLOCK at halo_exchange_3D.F90:883. (Historic decoy)\n")

                # 埋藏真正导致崩溃的 Rank
                if h_dir == target_dir_in_mpi and fname == target_file_in_mpi:
                    f.write(f"[{target_session}] [FATAL] [RANK_{target_rank}] DEADLOCK at halo_exchange_3D.F90:883. Process hanging.\n")
                    f.write(f"[{target_session}] [DUMP] CORE: {generate_hex_dump()}\n")

    # 3. 制造 Rank 映射 YAML 表
    volumes = [f"VOL_{i:03d}" for i in range(100)]
    all_ranks = list(range(1000, 9000))
    random.shuffle(all_ranks)
    
    # 确保 target_rank 在 target_volume 里
    if target_rank in all_ranks:
        all_ranks.remove(target_rank)
    
    chunk_size = 150
    chunks = [all_ranks[i:i + chunk_size] for i in range(0, len(all_ranks), chunk_size)]
    
    for i, vol in enumerate(volumes):
        mapping_file = os.path.join("rank_mappings", f"map_block_{i:03d}.yaml")
        
        assigned_ranks = chunks[i] if i < len(chunks) else []
        if vol == target_volume:
            assigned_ranks.append(target_rank)
            random.shuffle(assigned_ranks)

        data = {
            "metadata": {
                "generated_at": f"2023-11-{random.randint(10,15)}",
                "checksum": generate_hex_dump()[:8]
            },
            "volume_id": vol,
            "allocated_ranks": assigned_ranks
        }
        with open(mapping_file, "w") as f:
            yaml.dump(data, f)

    # 4. 制造 Base64 混淆的数据卷快照
    for vol in volumes:
        vol_dir = os.path.join("snapshot_volumes", vol)
        os.makedirs(vol_dir, exist_ok=True)
        dump_file = os.path.join(vol_dir, "grid_data.enc")
        
        with open(dump_file, "w") as f:
            # 写入大量干扰数据
            for _ in range(150):
                sess = random.choice(decoy_sessions + [target_session])
                r = random.randint(1000, 9000)
                v = random.choice(["U", "V", "Q", "T", "P", "W"])
                t, lev, lat, lon = random.randint(0, 200), random.randint(0, 64), random.randint(0, 360), random.randint(0, 1440)
                val = round(random.uniform(-100, 100), 4)
                
                # 随机生成一些正常 session 的 NaN 或者假目标
                if random.random() < 0.02:
                    val = "NaN_OVERFLOW"
                
                raw_str = f"RECORD::{sess}::RANK_{r}::VAR_{v}::COORD_{t}_{lev}_{lat}_{lon}::VAL_{val}"
                encoded = base64.b64encode(raw_str.encode('utf-8')).decode('utf-8')
                f.write(encoded + "\n")
            
            # 埋藏真正的炸弹
            if vol == target_volume:
                # 真实的
                target_str = f"RECORD::{target_session}::RANK_{target_rank}::VAR_T::COORD_{target_coords[0]}_{target_coords[1]}_{target_coords[2]}_{target_coords[3]}::VAL_NaN_OVERFLOW"
                f.write(base64.b64encode(target_str.encode('utf-8')).decode('utf-8') + "\n")
                
                # 同一个 Rank 其他变量的正常值（干扰）
                fake_str = f"RECORD::{target_session}::RANK_{target_rank}::VAR_U::COORD_{target_coords[0]}_{target_coords[1]}_{target_coords[2]}_{target_coords[3]}::VAL_45.21"
                f.write(base64.b64encode(fake_str.encode('utf-8')).decode('utf-8') + "\n")

    # 为了确保不直接裸露 JSON 文件，在 recovery 中放一个迷惑性的 readme
    with open("recovery/README.txt", "w") as f:
        f.write("Awaiting target.json for system restore...")

if __name__ == "__main__":
    build_sandbox()
