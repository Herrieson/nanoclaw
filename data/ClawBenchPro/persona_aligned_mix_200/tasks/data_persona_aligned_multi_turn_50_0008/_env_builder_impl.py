import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("config", exist_ok=True)
    os.makedirs("ecs_logs", exist_ok=True)
    os.makedirs("memory_dumps", exist_ok=True)

    # config
    config_data = {
        "max_allowed_fragment_gap_bytes": 256,
        "frame_time_redline_ms": 11.0,
        "suspicious_entity_count_max": 20
    }
    with open("config/engine_limits.json", "w") as f:
        json.dump(config_data, f, indent=4)

    # memory dumps (造假数据)
    # 我们要精确生成 总间隙(<=256) 为 2000 Bytes 的数据。
    # 策略：20个 gap = 100，外加一些 gap = 500 (不计入)
    start_addr = 0x1000 # 4096
    with open("memory_dumps/snapshot_v1.log", "w") as f:
        f.write("Alloc_ID,Start_Addr_Hex,Size_Bytes,Entity_ID\n")
        current_addr = start_addr
        alloc_id = 1
        
        # 生成 20 个计入碎片的 allocation
        for i in range(20):
            size = 64
            f.write(f"ALLOC_{alloc_id},{hex(current_addr)},{size},E_UNKNOWN\n")
            current_addr += size + 100 # gap is 100
            alloc_id += 1
            
        # 生成 5 个不计入碎片的 allocation (gap > 256)
        for i in range(5):
            size = 128
            f.write(f"ALLOC_{alloc_id},{hex(current_addr)},{size},E_UNKNOWN\n")
            current_addr += size + 400 # gap is 400
            alloc_id += 1

    # ecs logs
    with open("ecs_logs/profiler_session_01.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Tick", "System_Name", "Duration_ms", "Entities_Processed"])
        writer.writerow(["1", "PhysicsSolver", "15.2", "10"])  # 符合: 15.2 > 11.0 且 10 < 20 (混子)
        writer.writerow(["1", "CullingSystem", "12.0", "50"])  # 实体>=20, 不是
        writer.writerow(["2", "IKSystem", "11.5", "5"])        # 符合: 11.5 > 11.0 且 5 < 20 (混子)
        writer.writerow(["3", "AudioSystem", "2.0", "15"])     # 耗时 < 11.0, 不是

def build_turn_2():
    os.makedirs("physics", exist_ok=True)
    
    # 实体归属映射
    registry = {
        "PhysicsSolver": ["E_1001", "E_1002", "E_1003"],
        "IKSystem": ["E_2001", "E_2002"],
        "CullingSystem": ["E_3001"],
        "AudioSystem": ["E_4001"]
    }
    with open("physics/entity_registry.json", "w") as f:
        json.dump(registry, f, indent=4)
        
    # 增加额外的误导日志
    with open("ecs_logs/profiler_session_02_stress.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Tick", "System_Name", "Duration_ms", "Entities_Processed"])
        writer.writerow(["1", "PhysicsSolver", "25.0", "8"])
        writer.writerow(["2", "CullingSystem", "40.0", "15000"])

    # 碰撞对日志
    with open("physics/broadphase_pairs_t2.log", "w") as f:
        f.write("Entity_A,Entity_B,Collision_Type,Contact_Points\n")
        # 满足条件的：PhysicsSolver 的 E_1001, E_1003, 和 IKSystem 的 E_2001
        f.write("E_1001,E_9999,Mesh_to_Mesh,150\n")   # 命中 E_1001
        f.write("E_1002,E_8888,Sphere_to_Box,200\n")  # 错过 (非Mesh)
        f.write("E_2001,E_1003,Mesh_to_Mesh,105\n")   # 命中 E_2001, E_1003
        f.write("E_3001,E_7777,Mesh_to_Mesh,500\n")   # 错过 (CullingSystem不属于低效)
        f.write("E_2002,E_1001,Mesh_to_Mesh,80\n")    # 错过 (Contact_Points <= 100)

def build_turn_3():
    os.makedirs("memory_proposals", exist_ok=True)
    
    # rigid body updates
    with open("physics/rigid_body_updates.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Entity_ID", "Update_Size_Bytes", "Update_Freq_Hz"])
        writer.writerow(["E_1001", "100", "10"])
        writer.writerow(["E_1003", "50", "20"])
        writer.writerow(["E_2001", "210", "20"])
        writer.writerow(["E_1002", "500", "60"]) # 干扰数据
        writer.writerow(["E_3001", "1024", "144"]) # 干扰数据
        
    # allocator candidates
    # 根据之前设计的数值，Pool_Slim 是唯一解。
    candidates = [
        {"name": "Pool_Fat", "block_size": 256, "base_overhead": 500},
        {"name": "Pool_Fit", "block_size": 128, "base_overhead": 800},
        {"name": "Pool_Slim", "block_size": 64, "base_overhead": 1200},
        {"name": "Pool_Micro", "block_size": 32, "base_overhead": 3000}
    ]
    with open("memory_proposals/allocator_v2_candidates.json", "w") as f:
        json.dump(candidates, f, indent=4)

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
