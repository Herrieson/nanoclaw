import os
import random
import json

def build_env():
    # Set seed for reproducibility
    random.seed(6161)
    
    # Create directories for fragmented data
    for i in range(16):
        os.makedirs(f"logs/worker_{i:02d}", exist_ok=True)
        
    os.makedirs("vmem_table", exist_ok=True)
    os.makedirs("dumps/heap_regions", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Core target configuration
    target_vhandle = "0x8B3E4A10"
    target_region = "R-77"
    target_phy_addr = "0x8FFB2C40"
    target_entity = "8847291"
    target_dt = "183.2"

    sys_types = [
        "Physics.BroadPhase", "Physics.NarrowPhase", "Network.Sync", 
        "Resource.Load", "Script.Update", "Renderer.Cull"
    ]

    # 1. Generate Highly Fragmented Noise Logs
    for worker_id in range(16):
        with open(f"logs/worker_{worker_id:02d}/ecs_profile_20241120.log", "w") as f:
            for i in range(800):
                # Randomize time across the night
                hr = random.randint(1, 4)
                mnt = random.randint(0, 59)
                sec = random.randint(0, 59)
                ms = random.randint(0, 999)
                
                vhandle = f"0x{random.randint(0x10000000, 0x7FFFFFFF):08X}"
                sys_name = random.choice(sys_types)
                
                # Normal dt
                dt = round(random.uniform(0.1, 5.0), 2)
                
                # Injects decoys
                if random.random() < 0.05:
                    # Huge dt but wrong system
                    dt = round(random.uniform(150.0, 300.0), 2)
                    sys_name = random.choice(["Network.Sync", "Resource.Load", "Physics.BroadPhase"])
                elif random.random() < 0.05:
                    # Huge dt, NarrowPhase, but wrong time (e.g. 01:xx, 04:xx)
                    dt = round(random.uniform(150.0, 300.0), 2)
                    sys_name = "Physics.NarrowPhase"
                    hr = random.choice([1, 2, 4])
                
                log_line = f"2024-11-20T{hr:02d}:{mnt:02d}:{sec:02d}.{ms:03d}Z [Worker-{worker_id:02d}] SYS:{sys_name} vHandle={vhandle} dt={dt}ms\n"
                f.write(log_line)
                
                # Inject the real bottleneck exactly in worker 07
                if worker_id == 7 and i == 451:
                    spike_line = f"2024-11-20T03:12:47.999Z [Worker-07] SYS:Physics.NarrowPhase vHandle={target_vhandle} dt={target_dt}ms <WARN_FRAME_DROP>\n"
                    f.write(spike_line)

    # 2. Generate Page Tables (JSON fragments)
    all_mappings = []
    # Generate 5000 random mappings
    for _ in range(5000):
        v = f"0x{random.randint(0x10000000, 0x7FFFFFFF):08X}"
        r = f"R-{random.randint(0, 99):02d}"
        p = f"0x{random.randint(0x10000000, 0xFFFFFFFF):08X}"
        all_mappings.append((v, r, p))
    
    # Inject target mapping
    all_mappings.append((target_vhandle, target_region, target_phy_addr))
    random.shuffle(all_mappings)
    
    # Distribute mappings into 50 fragmented files
    chunk_size = len(all_mappings) // 50
    for page_idx in range(50):
        page_data = {}
        for v, r, p in all_mappings[page_idx*chunk_size : (page_idx+1)*chunk_size]:
            page_data[v] = {"region": r, "phy_addr": p}
            
        with open(f"vmem_table/page_{page_idx:02d}.json", "w") as f:
            json.dump(page_data, f, indent=2)

    # 3. Generate Dump Region Files
    for region_idx in range(100):
        region_id = f"R-{region_idx:02d}"
        with open(f"dumps/heap_regions/region_{region_id}.dat", "w") as f:
            f.write(f"=== HEAP REGION {region_id} ===\n")
            for chunk in range(150):
                is_target = (region_id == target_region and chunk == 87)
                
                if is_target:
                    addr = target_phy_addr
                    ent = target_entity
                    poly = 1899321
                else:
                    addr = f"0x{random.randint(0x10000000, 0xFFFFFFFF):08X}"
                    ent = str(random.randint(1000000, 9999999))
                    # Intentionally add some high-poly garbage chunks as decoys
                    if random.random() < 0.1:
                        poly = random.randint(1000000, 2000000)
                    else:
                        poly = random.randint(10, 8000)
                        
                chunk_type = random.choice(["RIGIDBODY_DAT", "BOX_COLLIDER_DAT", "MESH_COLLIDER_DAT"])
                
                f.write(f"====CHUNK_START:{addr}====\n")
                f.write(f"type: {chunk_type}\n")
                if poly > 500000:
                    f.write(f"warn: excessive_mesh_density_detected\n")
                f.write(f"  |--[ENT: {ent}]\n")
                f.write(f"  |--[POLY: {poly}]\n")
                f.write(f"====CHUNK_END====\n")

if __name__ == "__main__":
    build_env()
