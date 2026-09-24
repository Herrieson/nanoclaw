import os
import random

def build_env():
    # CWD 已经是 assets/data_persona_aligned_base_50_0020/
    os.makedirs("logs", exist_ok=True)
    os.makedirs("mem_dumps", exist_ok=True)

    random.seed(42)

    # 1. Generate ECS Logs
    # target archetype for spikes: ARCH_E7_DYNAMIC_MESH
    archetypes = [
        "ARCH_1A_STATIC_COLLIDER",
        "ARCH_2B_TRIGGER_VOLUME",
        "ARCH_3C_KINEMATIC_BODY",
        "ARCH_E7_DYNAMIC_MESH",
        "ARCH_9F_RAGDOLL_JOINT"
    ]

    with open("logs/ecs_tick.log", "w", encoding="utf-8") as f:
        f.write("=== PHY_SYS TICK LOGS (PROFILER DUMP) ===\n")
        f.write("FORMAT: [TICK_ID] | SYS: PhysSys | FrameTime_ms: <float> | ArchID: <hex_str> | Entities: <int> | CacheMiss: <int>\n\n")
        
        for tick_id in range(10000, 10500):
            arch = random.choice(archetypes)
            entities = random.randint(100, 5000)
            
            # Normal frame time
            frame_time = round(random.uniform(8.0, 16.5), 2)
            cache_miss = random.randint(100, 800)

            # Generate spikes only for ARCH_E7_DYNAMIC_MESH
            if arch == "ARCH_E7_DYNAMIC_MESH" and random.random() < 0.05:
                frame_time = round(random.uniform(52.1, 74.3), 2)
                cache_miss = random.randint(15000, 32000)
                
            log_line = f"[TICK {tick_id}] | SYS: PhysSys | FrameTime_ms: {frame_time} | ArchID: {arch} | Entities: {entities} | CacheMiss: {cache_miss}\n"
            f.write(log_line)

    # 2. Generate Arena Snapshot Dump
    # We will generate a bunch of memory segments. 
    # The target block will be owned by ARCH_E7_DYNAMIC_MESH and have the absolute highest 'F' count.
    
    # Decoy high fragment block (different archetype)
    decoy_address = "0x000001FA88000000"
    
    # Target high fragment block (correct archetype)
    target_address = "0x000002B47C90F000"

    with open("mem_dumps/arena_snapshot.dmp", "w", encoding="utf-8") as f:
        f.write(";; ROOT ARENA ALLOCATOR SNAPSHOT (v1.4.2)\n")
        f.write(";; LEGEND: [U]=USED, [F]=FRAGMENTED, [P]=PINNED, [Z]=ZEROED\n\n")
        
        for i in range(100):
            arch = random.choice(archetypes)
            base_addr = f"0x{random.randint(0x10000000000, 0x2FFFFFFFFFF):016X}"
            
            # Default layout generation
            layout_length = random.randint(20, 100)
            states = ["U", "P", "Z", "F"]
            weights = [0.6, 0.2, 0.1, 0.1]
            
            if i == 45:
                # Decoy block: Lots of 'F's but wrong archetype
                arch = "ARCH_1A_STATIC_COLLIDER"
                base_addr = decoy_address
                weights = [0.1, 0.0, 0.0, 0.9] 
                layout_length = 150 # Produces ~135 'F's
            elif i == 72:
                # TARGET block: Correct archetype, most 'F's
                arch = "ARCH_E7_DYNAMIC_MESH"
                base_addr = target_address
                weights = [0.05, 0.0, 0.0, 0.95]
                layout_length = 200 # Produces ~190 'F's (The max)
            elif arch == "ARCH_E7_DYNAMIC_MESH":
                # Other blocks for the target archetype, but low fragmentation
                weights = [0.7, 0.1, 0.1, 0.1]
                
            layout = "-".join(random.choices(states, weights=weights, k=layout_length))
            
            f.write(f">> SEG_HEAD: {base_addr} <<\n")
            f.write(f"[SYS_OWNER] PHYS_ENGINE\n")
            f.write(f"[ARCH_BIND] {arch}\n")
            f.write(f"[MEM_LAYOUT_MAP]\n")
            
            # Wrap layout for ugly formatting (mimicking hex editors/dumps)
            chunk_size = 40
            for j in range(0, len(layout), chunk_size):
                f.write(layout[j:j+chunk_size] + "\n")
                
            f.write(">> END_SEG <<\n\n")

if __name__ == "__main__":
    build_env()
