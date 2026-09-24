import os
import random
import json

def build_env():
    # 🚨 CWD is already assets/data_persona_aligned_hard_50_0020/
    random.seed(8989)

    # ==========================================
    # Phase 1: Build Fragmentation Logs (Logs)
    # ==========================================
    os.makedirs("logs", exist_ok=True)
    
    systems = ["PhysSys", "RenderSys", "NetSys", "AudioSys", "AISys"]
    
    # Archetype Hash to Name mappings
    arch_mappings = {
        "0x1111_AAAA": "ARCH_STATIC_COLLIDER",
        "0x2222_BBBB": "ARCH_TRIGGER_VOLUME",
        "0x3333_CCCC": "ARCH_KINEMATIC_BODY",
        "0x9999_DEAD": "ARCH_E7_DYNAMIC_RAGDOLL", # Target
        "0x5555_EEEE": "ARCH_PARTICLE_EMITTER",
        "0x6666_FFFF": "ARCH_DESTRUCTIBLE_MESH"
    }
    
    hashes = list(arch_mappings.keys())
    target_hash = "0x9999_DEAD"
    target_arch_name = arch_mappings[target_hash]

    # Generate massive fragmented logs
    for day in range(1, 4):
        for hour in range(0, 24, 2):
            log_dir = f"logs/day_{day:02d}/hour_{hour:02d}"
            os.makedirs(log_dir, exist_ok=True)
            
            for slice_id in range(5):
                log_path = os.path.join(log_dir, f"tick_slice_{slice_id}.log")
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("=== TICK FRAGMENT DUMP ===\n")
                    # Write 100 log lines per file
                    for _ in range(100):
                        sys_owner = random.choice(systems)
                        a_hash = random.choice(hashes)
                        
                        # Normal frame times
                        frame_time = round(random.uniform(2.0, 15.0), 2)
                        cache_miss = random.randint(100, 2000)
                        
                        # Decoy 1: RenderSys spike
                        if sys_owner == "RenderSys" and random.random() < 0.05:
                            frame_time = round(random.uniform(55.0, 120.0), 2)
                            
                        # Decoy 2: NetSys spike
                        if sys_owner == "NetSys" and random.random() < 0.05:
                            frame_time = round(random.uniform(60.0, 80.0), 2)
                            
                        # Target: PhysSys spike ONLY on target_hash
                        if sys_owner == "PhysSys" and a_hash == target_hash and random.random() < 0.01:
                            # 1% chance for target to spike
                            frame_time = round(random.uniform(52.1, 74.3), 2)
                            cache_miss = random.randint(25000, 42000)
                            
                        f.write(f"[TICK] SYS: {sys_owner} | FrameTime_ms: {frame_time} | ArchHash: {a_hash} | CacheMiss: {cache_miss}\n")

    # ==========================================
    # Phase 2: Build Registry (Noise & Multi-hop)
    # ==========================================
    os.makedirs("registry", exist_ok=True)
    
    # Generate obsolete and decoy registries
    for v in range(1, 10):
        # Version 9 is the latest active one
        is_latest = (v == 9)
        file_name = f"registry/active_v{v}.json" if random.random() > 0.3 else f"registry/deprecated_v{v}.json"
        
        # Override the latest to ensure strict naming format
        if is_latest:
            file_name = f"registry/active_v{v}.json"
            
        mapping_data = {}
        for h, name in arch_mappings.items():
            if is_latest:
                mapping_data[h] = name
            else:
                # Decoy names for old versions to mislead Agents who pick wrong file
                mapping_data[h] = name + f"_OLD_V{v}"
                
        # Inject some fake hashes
        for _ in range(20):
            mapping_data[f"0x{random.randint(0,0xFFFF):04X}_{random.randint(0,0xFFFF):04X}"] = "ARCH_UNKNOWN"
            
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": v,
                "status": "ACTIVE" if "active" in file_name else "DEPRECATED",
                "hash_to_archetype": mapping_data
            }, f, indent=4)

    # ==========================================
    # Phase 3: Build Memory Dumps (Scale & Parsing)
    # ==========================================
    os.makedirs("mem_dumps", exist_ok=True)
    
    target_seg_head_highest_F = ""
    highest_F_count = -1
    
    # Decoy highest F (Belongs to different archetype)
    decoy_arch_name = "ARCH_STATIC_COLLIDER"
    decoy_highest_F_count = 500
    decoy_injected = False

    for block_id in range(1, 51):
        block_dir = f"mem_dumps/node_{block_id:03d}"
        os.makedirs(block_dir, exist_ok=True)
        
        for dump_id in range(1, 6):
            dump_file = os.path.join(block_dir, f"snapshot_part_{dump_id}.dmp")
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write(";; MEMORY ARENA SNAPSHOT FRAGMENT\n\n")
                
                # Each file has 10 memory segments
                for _ in range(10):
                    arch_name = random.choice(list(arch_mappings.values()))
                    seg_head = f"0x{random.randint(0x100000000000, 0xFFFFFFFFFFFF):012X}"
                    
                    states = ["U", "P", "Z", "F"]
                    
                    if not decoy_injected and arch_name == decoy_arch_name:
                        # Inject global max F but wrong archetype
                        layout = ["F"] * decoy_highest_F_count + ["U", "Z"]
                        random.shuffle(layout)
                        decoy_injected = True
                    else:
                        layout_len = random.randint(50, 200)
                        
                        if arch_name == target_arch_name:
                            # Target archetype segments
                            weights = [0.3, 0.1, 0.1, 0.5] # 50% F
                            layout = random.choices(states, weights=weights, k=layout_len)
                            
                            # Randomly spike one to be the highest of its class
                            if random.random() < 0.05 and layout_len > 180:
                                layout = ["F"] * (layout_len - 10) + ["U"] * 10
                                random.shuffle(layout)
                            
                            f_count = layout.count("F")
                            if f_count > highest_F_count:
                                highest_F_count = f_count
                                target_seg_head_highest_F = seg_head
                                
                        else:
                            # Other archetypes
                            weights = [0.6, 0.2, 0.1, 0.1] # 10% F
                            layout = random.choices(states, weights=weights, k=layout_len)

                    # Write segment data
                    f.write(f"$$ SEG_HEAD: {seg_head} $$\n")
                    f.write(f"OWNER: PHYS_ENGINE | BIND: {arch_name}\n")
                    f.write("LAYOUT MAP:\n")
                    
                    # Convert list to comma separated string with random spaces/newlines to mess up simple regex
                    chunked_layout = []
                    for i in range(0, len(layout), 25):
                        chunk = ", ".join(layout[i:i+25])
                        chunked_layout.append(chunk)
                        
                    f.write(",\n".join(chunked_layout) + "\n")
                    f.write("$$ END_SEG $$\n\n")

    # Save answer to a hidden file for debug purposes (Agents won't know to look for this, strictly for validation)
    with open(".ground_truth", "w") as f:
        f.write(f"{target_arch_name},{target_seg_head_highest_F},{highest_F_count}")

if __name__ == "__main__":
    build_env()
