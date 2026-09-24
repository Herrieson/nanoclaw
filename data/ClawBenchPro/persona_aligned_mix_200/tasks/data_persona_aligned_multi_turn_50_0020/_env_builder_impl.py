import os
import argparse
import json
import csv
import random

def build_turn_1():
    # 1. config/archetypes.json - 实体组件组合映射
    os.makedirs("config", exist_ok=True)
    archetypes = {
        "A101": ["Transform", "MeshCollider", "Rigidbody", "NetworkSync"], # 罪魁祸首
        "A102": ["Transform", "SphereCollider", "Rigidbody"], # 干扰项：turn 1正常，turn 2退化
        "A103": ["Transform", "BoxCollider"], # 静态碰撞体，一直正常
        "A104": ["Transform", "CapsuleCollider", "CharacterController"] # 干扰项：turn 3引起OOM
    }
    with open("config/archetypes.json", "w") as f:
        json.dump(archetypes, f, indent=4)

    # 2. profiler_logs/frame_times.json - 帧耗时记录 (A101导致偶发 > 50ms)
    os.makedirs("profiler_logs", exist_ok=True)
    frames = []
    for i in range(1, 101):
        # 正常帧
        base_mesh = random.uniform(8.0, 12.0)
        base_sphere = random.uniform(2.0, 4.0)
        base_box = random.uniform(1.0, 2.0)
        
        # 偶发尖峰在特定帧 (15, 45, 82)
        if i in [15, 45, 82]:
            base_mesh = random.uniform(55.0, 65.0) # > 50ms redline

        frames.append({
            "frame_id": i,
            "systems": [
                {"name": "Physics.Narrowphase.Mesh", "archetype_id": "A101", "duration_ms": round(base_mesh, 2)},
                {"name": "Physics.Narrowphase.Sphere", "archetype_id": "A102", "duration_ms": round(base_sphere, 2)},
                {"name": "Physics.Broadphase.Static", "archetype_id": "A103", "duration_ms": round(base_box, 2)}
            ]
        })
    with open("profiler_logs/frame_times.json", "w") as f:
        json.dump(frames, f, indent=4)

    # 3. memory_dumps/allocations.csv - 内存碎片分配记录
    os.makedirs("memory_dumps", exist_ok=True)
    with open("memory_dumps/allocations.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Address", "Size_Bytes", "Archetype_ID", "Is_Contiguous"])
        # A101 (Mesh) - 大量碎片
        base_addr = 0x10000000
        for _ in range(5000):
            writer.writerow([hex(base_addr), 32, "A101", "False"])
            base_addr += 128 # 非连续
        # A102 (Sphere) - 少量连续大块
        writer.writerow([hex(0x20000000), 160000, "A102", "True"])
        # A103 (Box)
        writer.writerow([hex(0x30000000), 50000, "A103", "True"])

def build_turn_2():
    # 模拟 Turn 2，新增修复后的日志
    os.makedirs("new_profiler_logs", exist_ok=True)
    frames_v2 = []
    for i in range(101, 201):
        # Mesh 被修复了，非常稳定 (< 10ms)
        base_mesh = random.uniform(4.0, 6.0)
        # 陷阱：Sphere 因为共享底层的改变，发生了退化 (Regression!)，经常飙升到 60ms
        base_sphere = random.uniform(55.0, 68.0) if i % 10 == 0 else random.uniform(15.0, 20.0) 
        base_box = random.uniform(1.0, 2.0)
        
        frames_v2.append({
            "frame_id": i,
            "systems": [
                {"name": "Physics.Narrowphase.Mesh", "archetype_id": "A101", "duration_ms": round(base_mesh, 2)},
                {"name": "Physics.Narrowphase.Sphere", "archetype_id": "A102", "duration_ms": round(base_sphere, 2)},
                {"name": "Physics.Broadphase.Static", "archetype_id": "A103", "duration_ms": round(base_box, 2)}
            ]
        })
    with open("new_profiler_logs/frame_times.json", "w") as f:
        json.dump(frames_v2, f, indent=4)

    os.makedirs("new_memory_dumps", exist_ok=True)
    with open("new_memory_dumps/allocations.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Address", "Size_Bytes", "Archetype_ID", "Is_Contiguous"])
        # A101 (Mesh) - 碎片问题被修复，变成连续块
        writer.writerow([hex(0x40000000), 160000, "A101", "True"])
        # A102 (Sphere) - 为了支持新的池化，被迫拆分，出现退化迹象
        base_addr = 0x50000000
        for _ in range(2000):
            writer.writerow([hex(base_addr), 80, "A102", "False"])
            base_addr += 256
        writer.writerow([hex(0x30000000), 50000, "A103", "True"])

def build_turn_3():
    # 模拟 Turn 3，生产环境 OOM
    os.makedirs("prod_crash_logs", exist_ok=True)
    oom_trace = {
        "timestamp": "2024-05-12T10:00:00Z",
        "crash_reason": "OUT_OF_MEMORY",
        "total_allocated_mb": 4096,
        "active_blocks": [
            # A101 和 A102 其实内存占用正常，没泄漏
            {"archetype_id": "A101", "total_bytes": 160000, "leak_detected": False},
            {"archetype_id": "A102", "total_bytes": 160000, "leak_detected": False},
            # 陷阱：真正泄漏的是一直没管过的 A104 (Capsule CharacterController)，联机环境产生大量玩家
            {"archetype_id": "A104", "total_bytes": 4200000000, "leak_detected": True, "responsible_system": "Physics.Character.Kinematic"}
        ]
    }
    with open("prod_crash_logs/live_oom_trace.json", "w") as f:
        json.dump(oom_trace, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
