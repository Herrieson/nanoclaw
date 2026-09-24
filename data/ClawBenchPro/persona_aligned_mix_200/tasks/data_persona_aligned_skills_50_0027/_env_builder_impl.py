import os
import random
import string
import json

def generate_hex_dump():
    return " ".join(["0x" + "".join(random.choices(string.hexdigits.upper(), k=8)) for _ in range(8)])

def build_sandbox():
    os.makedirs("mpi_stdo", exist_ok=True)
    os.makedirs("nc_dumps", exist_ok=True)
    os.makedirs("recovery", exist_ok=True)
    os.makedirs(".system_config", exist_ok=True) # Hidden dir for LLM Mock Ground Truth

    nodes = 16
    ranks_per_node = 128
    
    # 动态生成 Ground Truth
    target_node = random.randint(5, 14)
    target_rank = target_node * ranks_per_node + random.randint(10, 110)
    
    target_time = random.randint(10, 40)
    target_lev = random.randint(20, 60)
    target_lat = random.randint(100, 300)
    target_lon = random.randint(400, 1000)

    # 将 Truth 写入隐藏配置文件，供 xarray_dask_cluster_skill 读取
    truth_data = {
        "deadlock_rank": target_rank,
        "anomaly_variable": "T",
        "coordinates": [target_time, target_lev, target_lat, target_lon]
    }
    with open(".system_config/truth.json", "w") as f:
        json.dump(truth_data, f)
    
    for node_id in range(nodes):
        # 1. Generate messy MPI stdout (Plain text, can be grepped)
        log_file = os.path.join("mpi_stdo", f"node_{node_id:02d}.log")
        with open(log_file, "w") as f:
            for i in range(500):
                rank = node_id * ranks_per_node + random.randint(0, ranks_per_node - 1)
                if random.random() < 0.2:
                    f.write(f"[2023-11-15T03:10:{random.randint(10,59)}Z] [NODE_{node_id}] MEM_DUMP {rank} : {generate_hex_dump()}\n")
                else:
                    f.write(f"[2023-11-15T03:11:{random.randint(10,59)}Z] [RANK_{rank}] MSG: Module dynamics_3d step {random.randint(1000, 9000)} OK. max_CFL=0.{random.randint(100, 999)}\n")
            
            # Injecting the deadlock error in the target node
            if node_id == target_node:
                f.write(f"[2023-11-15T03:12:45Z] [RANK_{target_rank}] FATAL_ERROR: MPI_Waitall() trapped in DEADLOCK at halo_exchange_3D.F90:883. Process hanging.\n")
                f.write(f"[2023-11-15T03:12:45Z] [RANK_{target_rank}] CORE_DUMP: {generate_hex_dump()} {generate_hex_dump()}\n")
                f.write(f"[2023-11-15T03:12:45Z] [RANK_{target_rank}] SIGABRT received. Syncing partial NetCDF buffers...\n")
                
            for i in range(100):
                rank = node_id * ranks_per_node + random.randint(0, ranks_per_node - 1)
                if rank != target_rank:
                    f.write(f"[2023-11-15T03:13:{random.randint(10,59)}Z] [RANK_{rank}] WARN: Timeout waiting for boundary data. MPI_Recv stalled.\n")

        # 2. Generate non-standard NetCDF dumps as BINARY files (Obstacle)
        nc_file = os.path.join("nc_dumps", f"grid_snapshot_n{node_id:02d}.nc.bin")
        with open(nc_file, "wb") as f:
            # 写入大量随机二进制数据，模拟真实的不可读 NetCDF 文件
            f.write(os.urandom(1024 * 50)) # 50KB dummy binary per file
            # 即使使用 strings 命令，也只能看到乱码，强制要求使用特定的 API 工具

if __name__ == "__main__":
    build_sandbox()
