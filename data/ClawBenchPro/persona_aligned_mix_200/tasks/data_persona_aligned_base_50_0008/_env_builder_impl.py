import os
import random

def build_env():
    # Set seed for reproducibility in sandbox generation
    random.seed(6161)
    
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    target_addr = "0x8FFB2C40"
    target_entity = "8847291"
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

    # 2. Generate custom structured memory dump (non-standard text format)
    with open("dumps/mem_snapshot.dat", "w") as f:
        f.write("=========================================\n")
        f.write("HEADER::PHYSICS_MEM_SNAP_v3.4_NATIVE\n")
        f.write("MODE::FRAG_DUMP\n")
        f.write("=========================================\n")
        
        for i in range(1500):
            if i == 842:
                addr = target_addr
                ent = target_entity
                poly = 1899321 # Extremely high poly count
                chunk_type = "MESH_COLLIDER_DAT"
            else:
                addr = f"0x{random.randint(0x10000000, 0x7FFFFFFF):08X}"
                ent = str(random.randint(1000000, 9999999))
                poly = random.randint(10, 8000)
                chunk_type = random.choice(["RIGIDBODY_DAT", "BOX_COLLIDER_DAT", "SPHERE_COLLIDER_DAT", "MESH_COLLIDER_DAT"])
            
            f.write(f"====CHUNK_START:{addr}====\n")
            f.write(f"type: {chunk_type}\n")
            f.write(f"alloc_id: {random.randint(100, 999)}\n")
            f.write(f"count: 1\n")
            
            if poly > 500000:
                f.write(f"warn: large_allocation_detected\n")
                f.write(f"sys_trace: 0x{random.randint(0x100000, 0xFFFFFF):06X} -> 0x{random.randint(0x100000, 0xFFFFFF):06X}\n")
                
            f.write(f"  |--[ENT: {ent}] [PTR: 0x{random.randint(0x1000, 0xFFFF):04X}] -> POLY: {poly}\n")
            f.write(f"  |--[DIRTY_FLAG: {random.choice(['true', 'false'])}]\n")
            f.write(f"====CHUNK_END====\n")

if __name__ == "__main__":
    build_env()
