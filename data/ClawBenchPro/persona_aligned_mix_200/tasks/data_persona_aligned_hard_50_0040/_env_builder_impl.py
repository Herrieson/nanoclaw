import os
import random
import json

def build_env():
    # 初始化环境目录
    os.makedirs("logs/ecs_shards", exist_ok=True)
    os.makedirs("registry/comps", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 目标关键数据 - 整个废土环境的唯一真理
    target_eid = "0x7C9A"
    target_comp_id = "COMP_882"
    target_ptr = "0x0B88F1A0"
    target_dt = 42.7  # 大于 16.6ms
    target_size = 131072
    
    random.seed(4242)

    # ==========================================
    # 1. 制造日志碎片 (Logs)
    # ==========================================
    systems = [
        "Sys_Render_Mesh_Instancing", 
        "Sys_AI_Pathing_NavMesh", 
        "Sys_Audio_Spatial_Mix", 
        "Sys_Physics_Collision", 
        "Sys_Network_State_Sync",
        "Sys_Anim_IK_Solver"
    ]
    
    target_injected = False
    
    for shard_idx in range(1, 151): # 150 个碎片文件
        shard_entries = []
        for i in range(250): # 每个文件 250 条日志 = 总计 37500 条
            sys = random.choice(systems)
            eid = f"0x{random.randint(0x1000, 0xFFFF):04X}"
            comp_id = f"COMP_{random.randint(100, 999)}"
            dt = round(random.uniform(0.1, 8.5), 2)
            
            # 制造一些非物理模块的高耗时干扰
            if random.random() < 0.05:
                dt = round(random.uniform(18.0, 55.0), 2)
                if sys == "Sys_Physics_Collision":
                    sys = "Sys_Render_Mesh_Instancing" # 避免破坏唯一性
            
            # 植入目标 (确保只植入一次)
            if not target_injected and shard_idx == 73 and i == 114:
                sys = "Sys_Physics_Collision"
                eid = target_eid
                comp_id = target_comp_id
                dt = target_dt
                target_injected = True
                
            # 脏乱差的日志格式，混合多种分隔符和乱码
            thread_id = random.randint(0, 31)
            noise_prefix = f"~#0x{random.randint(0, 99999):05X}&"
            entry = f"[{shard_idx:03d}-{i:04d}] {noise_prefix} <T_{thread_id}> | MODULE=[{sys}] ---> EXEC_STATUS:OK || EID={eid} :: {comp_id} || CPU_CYCLES:{random.randint(1000, 99999)} --- METRICS:: DT:{dt}ms | NO_PTR_STORED"
            shard_entries.append(entry)
            
        with open(f"logs/ecs_shards/shard_{shard_idx:03d}.log", "w", encoding="utf-8") as f:
            f.write("\n".join(shard_entries))

    # ==========================================
    # 2. 构造注册表 JSON 映射表 (Registry)
    # ==========================================
    for comp_idx in range(100, 1000): # COMP_100 到 COMP_999
        comp_name = f"comp_{comp_idx}"
        allocations = {}
        
        # 为每个组件随机生成一些内存映射
        for _ in range(random.randint(20, 50)):
            r_eid = f"0x{random.randint(0x1000, 0xFFFF):04X}"
            r_ptr = f"0x{random.randint(0x01000000, 0x0FFFFFFF):08X}"
            allocations[r_eid] = {
                "ptr": r_ptr,
                "status": random.choice(["active", "sleeping", "destroyed"]),
                "last_accessed": random.randint(100000, 900000)
            }
            
        # 植入目标到对应的 COMP JSON
        if comp_name == target_comp_id.lower():
            allocations[target_eid] = {
                "ptr": target_ptr,
                "status": "active_fatal",
                "last_accessed": 999999
            }
            
        with open(f"registry/comps/{comp_name}.json", "w", encoding="utf-8") as f:
            json.dump({
                "schema": "v3_mem_map",
                "component_id": comp_name.upper(),
                "allocations": allocations,
                "meta": "auto_generated"
            }, f, indent=2)

    # ==========================================
    # 3. 构造海量混淆的 Dump 快照 (Dumps)
    # ==========================================
    dump_files = ["mem_frag_0x8E.dump", "mem_frag_0x8F.dump", "mem_frag_0x90.dump", "engine_crash.dump.bak"]
    
    for dump_name in dump_files:
        dump_entries = []
        dump_entries.append(f"==== TITAN_ENGINE MEMORY SNAPSHOT [{dump_name}] ====\n")
        
        is_target_dump = (dump_name == "mem_frag_0x8F.dump")
        target_dumped = False
        
        for i in range(1200): # 每个 dump 包含 1200 个内存块
            block_ptr = f"0x{random.randint(0x01000000, 0x0FFFFFFF):08X}"
            size = random.choice([256, 512, 1024, 2048, 4096, 8192, 16384])
            status = random.choice(["FRAGMENTED", "ORPHANED", "LOCKED_READ"])
            
            # 在 0x8E 里制造同指针假象，但大小不同
            if not is_target_dump and not target_dumped and i == 450:
                block_ptr = target_ptr
                size = 128 # 错误大小
                target_dumped = True
                
            # 在真实的 0x8F 植入正确大小
            if is_target_dump and not target_dumped and i == 872:
                block_ptr = target_ptr
                size = target_size
                status = "OOM_FATAL_LEAK"
                target_dumped = True
                
            hex_dump = " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)])
            
            dump_entries.append(f">>> MEM_REGION_START <<<")
            dump_entries.append(f"      BASE_ADDR: {block_ptr}")
            dump_entries.append(f"      STAT: {status} | BLK_SIZE_BYTES: {size}")
            dump_entries.append(f"      PREVIEW: {hex_dump} ...")
            dump_entries.append(f">>> MEM_REGION_END <<<\n")
            
        with open(f"dumps/{dump_name}", "w", encoding="utf-8") as f:
            f.write("\n".join(dump_entries))

if __name__ == "__main__":
    build_env()
