import os
import random

def build_env():
    # 确保所需目录存在
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
    # 构造不可读取的二进制 Dump 文件 (物理降维障碍)
    # ==========================================
    # Agent 无法再像原题那样直接读取文件进行 grep，必须依赖 Skill
    dummy_binary_data = bytearray(random.getrandbits(8) for _ in range(4096))
    
    with open("dumps/mem_frag_0x8F.bin", "wb") as f:
        f.write(dummy_binary_data)

if __name__ == "__main__":
    build_env()
