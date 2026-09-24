import os
import random
import json
from datetime import datetime, timedelta

def build_env():
    # 建立多级废土目录结构
    os.makedirs("telemetry", exist_ok=True)
    os.makedirs("fix_list", exist_ok=True)
    
    # 核心设定
    crash_time = datetime(2024, 3, 15, 2, 47, 19, 550000)
    crash_time_str = crash_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    target_tick_id = 8945231
    target_dt = 1284.55 # 极其夸张的 1.2秒的卡顿
    
    # 活跃实体ID（真凶隐藏其中）
    awake_entities = ["0x88A1", "0x3F2B", "0xDEAD", "0x112C", "0x77A0"]
    culprit_entity = "0xDEAD"
    culprit_asset = "assets/models/cinematics/boss_titan_shatter_piece_HD_LOD0.mesh"
    culprit_vtx = 18543021
    
    # 诱饵设定（极高顶点数，但并未在死锁帧活跃）
    decoy_entities = ["0x9999", "0xAAAA", "0xBBBB"]
    decoy_asset = "assets/models/environment/super_mountain_background_static.mesh"
    decoy_vtx = 65000000 # 比真凶还要高！
    
    # 1. 生成看门狗报告
    watchdog_data = {
        "event": "CRITICAL_PROCESS_HANG",
        "severity": "FATAL",
        "details": {
            "trigger": "Watchdog Timeout",
            "threshold_ms": 1000,
            "detected_at": f"{crash_time_str}Z",
            "culprit_thread": "PHYSX_WORKER_0",
            "status": "Dump generation forced. Process terminated."
        }
    }
    with open("telemetry/watchdog_crash.json", "w") as f:
        json.dump(watchdog_data, f, indent=4)
        
    # 2. 生成碎裂的日志文件 (10个节点，每个节点 100 个文件，共 1000 个文件，20000行日志)
    base_time = crash_time - timedelta(seconds=15)
    current_tick = target_tick_id - 10000
    
    for node in range(10):
        node_dir = f"logs/physx_nodes/node_{node:02d}"
        os.makedirs(node_dir, exist_ok=True)
        
        for frag in range(100):
            with open(f"{node_dir}/tick_frag_{frag:03d}.log", "w", encoding="utf-8") as f:
                f.write("## TRACE_LEVEL=INFO ## NODE_ROUTING_KEY=PHYSX\n")
                for _ in range(20):
                    current_tick += 1
                    base_time += timedelta(milliseconds=16.6) # 模拟 60帧推进
                    
                    # 植入致命卡死帧
                    if current_tick == target_tick_id:
                        log_time = crash_time_str
                        dt = target_dt
                        ents = awake_entities
                        f.write(f"[{log_time}] TICK: {current_tick} | THREAD: PHYSX_0 | DT={dt}ms | AWAKE_ENTITIES=[{', '.join(ents)}]\n")
                    else:
                        # 正常帧或小毛刺
                        log_time = base_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        dt = round(random.uniform(0.5, 12.0), 2)
                        
                        # 偶尔出现诱饵小卡顿（50-80ms）包含诱饵实体，混淆视听
                        if random.random() < 0.005:
                            dt = round(random.uniform(50.0, 80.0), 2)
                            ents = decoy_entities + [f"0x{random.randint(0x1000, 0x8000):04X}"]
                        else:
                            ents_count = random.randint(1, 5)
                            ents = [f"0x{random.randint(0x1000, 0x8000):04X}" for _ in range(ents_count)]
                            
                        f.write(f"[{log_time}] TICK: {current_tick} | THREAD: PHYSX_0 | DT={dt}ms | AWAKE_ENTITIES=[{', '.join(ents)}]\n")

    # 3. 生成凌乱的 ECS 内存快照
    def generate_entity_block(eid, is_culprit=False, is_decoy=False):
        vtx = random.randint(10, 500)
        asset = f"assets/props/box_{random.randint(1,20)}.mesh"
        is_kinematic = "true" if random.random() > 0.8 else "false"
        
        if is_culprit:
            vtx = culprit_vtx
            asset = culprit_asset
            is_kinematic = "false"
        elif is_decoy:
            vtx = decoy_vtx
            asset = decoy_asset
            is_kinematic = "true" # 诱饵往往是静态的
            
        block = f"PAGE_OFFSET 0x{random.randint(0x1000, 0xFFFF):04X}\n"
        block += f"<EID: {eid}> {{\n"
        block += f"    [0x00] Flags: 0x{random.randint(0,255):02X} | Generation: {random.randint(1,10)}\n"
        if random.random() < 0.1:
            block += "    >> WARN: MEMORY PAGE FAULT DETECTED IN THIS BLOCK <<\n"
        block += f"    [0x1C] MeshData {{ Asset: \"{asset}\", Vtx: {vtx}, Mat: \"mat_default\" }}\n"
        block += f"    [0x38] RigidBody {{ active: {'true' if not is_decoy else 'false'}, kinematic: {is_kinematic}, mass: {random.uniform(1.0, 1000.0):.2f} }}\n"
        block += "}\n\n"
        return block

    # 准备所有要写入的实体
    all_blocks = []
    
    # 填充真凶和当帧的替罪羊
    for eid in awake_entities:
        all_blocks.append(generate_entity_block(eid, is_culprit=(eid==culprit_entity)))
        
    # 填充超高顶点的诱饵
    for eid in decoy_entities:
        all_blocks.append(generate_entity_block(eid, is_decoy=True))
        
    # 填充大量噪音实体 (总计 5000 个实体，打碎放入不同文件)
    for _ in range(5000):
        eid = f"0x{random.randint(0x1000, 0x8000):04X}"
        if eid not in awake_entities and eid not in decoy_entities:
            all_blocks.append(generate_entity_block(eid))
            
    random.shuffle(all_blocks)
    
    # 将实体分布到 16 个 arena，每个 arena 有 5 个 page
    blocks_per_page = len(all_blocks) // 80
    
    for arena in range(16):
        arena_dir = f"memory_dumps/arena_{arena:02d}"
        os.makedirs(arena_dir, exist_ok=True)
        
        for page in range(5):
            page_idx = arena * 5 + page
            start_idx = page_idx * blocks_per_page
            # 最后一个 page 拿走所有剩余的
            end_idx = (start_idx + blocks_per_page) if page_idx < 79 else len(all_blocks)
            
            with open(f"{arena_dir}/page_{page:02d}.mem", "w", encoding="utf-8") as f:
                f.write(f"=== ARENA {arena} PAGE {page} ===\n")
                f.write(f"DUMP_TIMESTAMP: {crash_time_str}\n\n")
                for block in all_blocks[start_idx:end_idx]:
                    f.write(block)

if __name__ == "__main__":
    build_env()
