import os
import random

def build_env():
    # 确保所需目录存在，由于系统已设定 cwd 为 assets/data_persona_aligned_base_50_0040/，直接使用相对路径
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # ==========================================
    # 构造极具干扰性的 ECS Profiling 日志
    # ==========================================
    log_entries = []
    systems = [
        "Sys_Render_Mesh_Instancing", 
        "Sys_AI_Pathing_NavMesh", 
        "Sys_Audio_Spatial_Mix", 
        "Sys_Physics_Collision", 
        "Sys_Network_State_Sync",
        "Sys_Anim_IK_Solver"
    ]
    
    # 目标答案数据（Agent需要推导并提取这些信息）
    target_eid = "0x7C9A"
    target_ptr = "0x0B88F1A0"
    target_dt = 42.7  # 远超 16.6ms 的物理碰撞耗时
    target_size = 16384

    # 混淆数据生成
    random.seed(42)  # 固定种子以保证评测的一致性
    
    for i in range(800):
        sys = random.choice(systems)
        eid = f"0x{random.randint(0x1000, 0x9000):04X}"
        ptr = f"0x{random.randint(0x01000000, 0x09000000):08X}"
        # 正常帧耗时通常在 0.1 到 5.5 ms 之间
        dt = round(random.uniform(0.1, 5.5), 2)
        
        # 植入目标异常点
        if i == 512:
            sys = "Sys_Physics_Collision"
            eid = target_eid
            ptr = target_ptr
            dt = target_dt
            
        # 制造一些非物理模块的假高耗时干扰（如渲染或AI，不满足 Sys_Physics_Collision 的条件）
        if i in [120, 340, 670]:
            dt = round(random.uniform(18.0, 30.0), 2)
            if sys == "Sys_Physics_Collision":
                sys = "Sys_Render_Mesh_Instancing"
        
        # 采用极其非标准且难以简单正则化的日志格式
        timestamp = f"[00:0{i//60}:{i%60:02d}.{random.randint(100,999):03d}]"
        # 故意混用不同的分隔符
        entry = f"{timestamp} ~~ {{ CORE_THREAD_0{random.randint(1,4)} }} ~~ [ {sys} ] >> EID<{eid}> ---> DT:{dt}ms ||| MEM_PTR:{ptr}"
        log_entries.append(entry)

    with open("logs/ecs_profiler.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries))
        
    # ==========================================
    # 构造自定义结构的内存碎片 Dump 文件
    # ==========================================
    dump_entries = []
    dump_entries.append("==== TITAN_ENGINE MEMORY FRAGMENTATION SNAPSHOT v2.14 ====\n")
    dump_entries.append("WARN: Partial dump due to SEGFAULT risk.\n")
    
    for i in range(150):
        block_ptr = f"0x{random.randint(0x01000000, 0x09000000):08X}"
        size = random.choice([256, 512, 1024, 2048, 4096])
        status = random.choice(["FRAGMENTED", "ORPHANED", "LOCKED_READ"])
        
        # 植入对应的目标内存块
        if i == 103:
            block_ptr = target_ptr
            size = target_size
            status = "ALLOC_FATAL_OOM"
        
        hex_dump = " ".join([f"{random.randint(0, 255):02X}" for _ in range(16)])
        
        # 非标准的层级文本格式
        dump_entries.append(f"@@@ MEM_REGION_START @@@")
        dump_entries.append(f"    BASE_ADDR: {block_ptr}")
        dump_entries.append(f"    STAT: {status} | BLK_SIZE_BYTES: {size}")
        dump_entries.append(f"    RAW_HEX_PREVIEW: {hex_dump}")
        dump_entries.append(f"@@@ MEM_REGION_END @@@\n")
        
    with open("dumps/mem_frag_0x8F.dump", "w", encoding="utf-8") as f:
        f.write("\n".join(dump_entries))

if __name__ == "__main__":
    build_env()
