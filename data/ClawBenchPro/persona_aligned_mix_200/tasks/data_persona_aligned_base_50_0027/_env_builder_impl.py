import os
import random
import string

def generate_hex_dump():
    return " ".join(["0x" + "".join(random.choices(string.hexdigits.upper(), k=8)) for _ in range(8)])

def build_sandbox():
    os.makedirs("mpi_stdo", exist_ok=True)
    os.makedirs("nc_dumps", exist_ok=True)
    os.makedirs("recovery", exist_ok=True)

    nodes = 16
    ranks_per_node = 128
    
    target_node = 11
    target_rank = target_node * ranks_per_node + 87  # Rank 1495
    
    target_time = 24
    target_lev = 39
    target_lat = 180
    target_lon = 720
    
    for node_id in range(nodes):
        # Generate messy MPI stdout
        log_file = os.path.join("mpi_stdo", f"node_{node_id:02d}.log")
        with open(log_file, "w") as f:
            for i in range(500):
                # Random interleaving of normal steps and garbage
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

        # Generate non-standard NetCDF dump representations
        nc_file = os.path.join("nc_dumps", f"grid_snapshot_n{node_id:02d}.raw")
        with open(nc_file, "w") as f:
            f.write("### NCDUMP RAW EXTRACT (UNFORMATTED) ###\n")
            f.write("### DIMENSION ORDER: [time, lev, lat, lon] ###\n\n")
            for _ in range(300):
                r = node_id * ranks_per_node + random.randint(0, ranks_per_node - 1)
                t = random.randint(0, 48)
                lev = random.randint(0, 64)
                lat = random.randint(0, 360)
                lon = random.randint(0, 1440)
                var = random.choice(["U", "V", "Q", "T", "P"])
                val = round(random.uniform(-50.0, 300.0), 4)
                f.write(f"@@DATA_BLK || R_ID:{r} | VAR:{var} || COORD>[{t}, {lev}, {lat}, {lon}] == {val}\n")
                
            if node_id == target_node:
                # Injecting the anomaly
                f.write(f"@@DATA_BLK || R_ID:{target_rank} | VAR:U || COORD>[{target_time}, {target_lev}, {target_lat}, {target_lon}] == 12.4501\n")
                f.write(f"@@DATA_BLK || R_ID:{target_rank} | VAR:T || COORD>[{target_time}, {target_lev}, {target_lat}, {target_lon}] == NaN_OVERFLOW_0xDEADBEEF\n")
                f.write(f"@@DATA_BLK || R_ID:{target_rank} | VAR:Q || COORD>[{target_time}, {target_lev}, {target_lat}, {target_lon}] == 0.0001\n")

if __name__ == "__main__":
    build_sandbox()
