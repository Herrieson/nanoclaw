import os
import random
import struct

def build_env():
    # Set seed for reproducibility in sandbox generation
    random.seed(6161)
    
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    target_addr = "0x8FFB2C40"
    target_dt = "183.2"

    # 1. Generate extremely noisy ECS Profiling Logs
    with open("logs/ecs_profile.log", "w") as f:
        for i in range(3000):
            tick = 145000 + i
            addr = f"0x{random.randint(0x10000000, 0x7FFFFFFF):08X}"
            dt = round(random.uniform(0.01, 3.50), 2)
            sys_name = random.choice([
                "Physics.Step", 
                "BroadPhase_BVH", 
                "Solver_Iterations", 
                "Integrate_Velocities",
                "Raycast_Batch"
            ])
            worker_id = random.randint(0, 15)
            
            log_line = f"2024-11-20T03:11:{i%60:02d}.{random.randint(100,999)}Z [Worker-{worker_id:02d}] SYS:{sys_name} (addr={addr}) tick={tick} dt={dt}ms\n"
            f.write(log_line)

            # Inject the bottleneck spike
            if i == 2154:
                spike_line = f"2024-11-20T03:11:{i%60:02d}.999Z [Worker-03] SYS:NarrowPhase_Mesh (addr={target_addr}) tick={tick} dt={target_dt}ms <WARN_FRAME_DROP_DETECTED>\n"
                f.write(spike_line)

    # 2. Generate a totally obscured binary dump file
    # This replaces the original readable .dat file, forcing the use of specific skills
    # We will just write garbage and header bytes to make it look like a valid bin file
    with open("dumps/mem_snapshot.bin", "wb") as f:
        # Fake Magic Header for PHYSICS_MEM_SNAP_v3.4_NATIVE
        f.write(b"PHYS_SNAP_v3.4_NAT\x00\x00")
        f.write(b"\x01\x00\x00\x00") # Mode
        
        # Write random binary garbage to simulate 10MB of memory chunks
        for _ in range(5000):
            # random floats and ints
            f.write(struct.pack('f', random.uniform(0, 100)))
            f.write(struct.pack('i', random.randint(0, 9999999)))
            f.write(os.urandom(64)) # random bytes payload

if __name__ == "__main__":
    build_env()
