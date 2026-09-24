import os
import random

def build_env():
    # 创建目录结构
    os.makedirs("dumps/perf", exist_ok=True)
    os.makedirs("dumps/mem", exist_ok=True)
    os.makedirs("fix_list", exist_ok=True)

    # 预设特定数据
    spike_tick_id = 45892
    spike_entities = ["0x1A4F", "0x88B2", "0xDEAD", "0x9C01", "0x00F3"]
    culprit_entity = "0x9C01"
    culprit_asset = "environments/ruins/statue_shattered_piece_04_cinematic.mesh"

    # 1. 生成物理 Tick 日志 (physics_ticks.log)
    with open("dumps/perf/physics_ticks.log", "w", encoding="utf-8") as f:
        f.write("=== PHYSX THREAD PROFILING LOG ===\n")
        f.write("FORMAT: [TIMESTAMP] TICK_ID | DT=<val>ms | ACTIVE_BODIES=[...]\n")
        
        for i in range(45800, 46000):
            # 随机生成一些正常帧的时间
            dt = round(random.uniform(0.8, 4.5), 2)
            active_count = random.randint(2, 6)
            entities = [f"0x{random.randint(0x1000, 0xFFFF):04X}" for _ in range(active_count)]
            
            # 植入性能毛刺帧
            if i == spike_tick_id:
                dt = 284.53
                entities = spike_entities
                f.write(f"[10:43:21.054] {i} | DT={dt}ms | ACTIVE_BODIES=[{', '.join(entities)}]\n")
            else:
                f.write(f"[10:43:{(20 + i*0.016):.3f}] {i} | DT={dt}ms | ACTIVE_BODIES=[{', '.join(entities)}]\n")

    # 2. 生成 ECS 内存快照 (ecs_snapshot.dat)
    # 使用一种非标准的、类似 C++ 结构体 dump 的花式格式，混杂干扰数据
    ecs_content = []
    ecs_content.append("## MEMORY DUMP: ECS MANAGER (ARENA 0x04) ##")
    ecs_content.append("## WARN: Partial page faults detected at 0x08F4A000 ##\n")

    def generate_entity_block(eid, is_culprit=False):
        vtx_count = random.randint(8, 256)
        mesh_asset = f"core/primitives/box_{random.randint(1,10)}.mesh"
        mass = round(random.uniform(5.0, 50.0), 1)
        
        if is_culprit:
            vtx_count = 14508392  # 极其夸张的顶点数
            mesh_asset = culprit_asset
            mass = 5000.0

        block = f"Ptr<0x{random.randint(0x100000, 0x9FFFFF):06X}>: <Entity id={eid}> {{\n"
        block += f"  [0x00] DirtyFlags: 0x{random.randint(0, 255):02X}\n"
        block += f"  [0x04] Transform {{ pos: [{random.uniform(-100, 100):.1f}, {random.uniform(0, 50):.1f}, {random.uniform(-100, 100):.1f}], rot: [0, 0, 0, 1] }}\n"
        block += f"  [0x20] RigidBody {{ mass: {mass}, kinematic: false, sleeping: false, vel: [0.0, -9.81, 0.0] }}\n"
        
        # 加入一些随机乱码干扰
        if random.random() > 0.8:
            block += "  [0x38] ++ SEGFAULT READ ++ \\xDE\\xAD\\xBE\\xEF\n"
            
        block += f"  [0x40] Collider {{ type: ConvexMesh, AssetPath: \"{mesh_asset}\", Vtx: {vtx_count}, bnd_rad: {random.uniform(1.0, 100.0):.1f} }}\n"
        block += "}\n"
        return block

    # 填充大量正常实体
    for _ in range(150):
        rand_eid = f"0x{random.randint(0x1000, 0xFFFF):04X}"
        if rand_eid not in spike_entities:
            ecs_content.append(generate_entity_block(rand_eid))

    # 混入毛刺帧涉及的实体
    for eid in spike_entities:
        ecs_content.append(generate_entity_block(eid, is_culprit=(eid == culprit_entity)))

    # 打乱快照顺序，模拟内存碎片分布
    blocks = ecs_content[2:]
    random.shuffle(blocks)
    
    with open("dumps/mem/ecs_snapshot.dat", "w", encoding="utf-8") as f:
        f.write(ecs_content[0] + "\n")
        f.write(ecs_content[1] + "\n")
        for block in blocks:
            f.write(block)
            
if __name__ == "__main__":
    build_env()
