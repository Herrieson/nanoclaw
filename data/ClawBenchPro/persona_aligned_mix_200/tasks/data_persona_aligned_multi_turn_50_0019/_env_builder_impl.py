import os
import argparse
import json

def build_turn_1():
    os.makedirs("traces", exist_ok=True)
    os.makedirs("ecs_data", exist_ok=True)

    csv_content = """Entity_ID,Entity_Name,Collision_Layer,Rigid_Body_Type,Chunk_ID
101,Crate_A,Layer_Destructible,Dynamic,Chunk_A
102,Crate_B,Layer_Destructible,Dynamic,Chunk_A
103,Vehicle_Tank,Layer_Vehicle,Kinematic,Chunk_B
104,Water_Volume,Layer_Water,Static,Chunk_B
105,Wall_Fragment,Layer_Destructible,Dynamic,Chunk_C
106,Trigger_Zone,Layer_Invisible,Static,Chunk_C
201,Barrel_Red,Layer_Destructible,Dynamic,Chunk_A
"""
    with open("ecs_data/entities.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    traces = {
        "frame_001.log": "[PROFILER] Frame: 1 | DT: 14.2ms | ActiveEntities: 101,104,106\n[PHYSICS] Solver completed.\n",
        "frame_002.log": "[PROFILER] Frame: 2 | DT: 18.5ms | ActiveEntities: 101,102,103,104,105,106,201\n[PHYSICS] Spikes detected!\n",
        "frame_003.log": "[PROFILER] Frame: 3 | DT: 15.1ms | ActiveEntities: 101,106,201\n[PHYSICS] Solver completed.\n",
        "frame_004.log": "[PROFILER] Frame: 4 | DT: 19.2ms | ActiveEntities: 102,103,105,201\n[PHYSICS] Spikes detected!\n",
        "frame_005.log": "[PROFILER] Frame: 5 | DT: 21.0ms | ActiveEntities: 102,103,105\n[PHYSICS] Major spikes detected!\n",
        "frame_006.log": "[PROFILER] Frame: 6 | DT: 16.0ms | ActiveEntities: 103,104,105,106\n[PHYSICS] Solver completed.\n"
    }
    
    # 逻辑陷阱说明：
    # DT > 16.6 的帧是 frame_002, frame_004, frame_005。
    # 存在于所有这些掉帧中的实体是 102, 103, 105。
    # (104在002出现，但不在004,005；201在002,004出现，但不在005)

    for fname, content in traces.items():
        with open(os.path.join("traces", fname), "w", encoding="utf-8") as f:
            f.write(content)

def build_turn_2():
    os.makedirs("memory_dumps", exist_ok=True)
    
    alloc_trace = []
    
    # 102: Lagger, but low memory allocs (Trap: only 5 allocs)
    for _ in range(5):
        alloc_trace.append({"Entity_ID": 102, "Op": "ALLOC", "Size": 64})
        
    # 103: Lagger AND high memory allocs (Target 1: 35 allocs)
    for _ in range(35):
        alloc_trace.append({"Entity_ID": 103, "Op": "ALLOC", "Size": 256})
        
    # 104: Not a lagger (from T1), but EXTREME memory allocs (Trap: 100 allocs)
    for _ in range(100):
        alloc_trace.append({"Entity_ID": 104, "Op": "ALLOC", "Size": 128})
        
    # 105: Lagger AND high memory allocs (Target 2: 25 allocs)
    for _ in range(25):
        alloc_trace.append({"Entity_ID": 105, "Op": "ALLOC", "Size": 32})
        
    # 201: Low mem, just some noise
    for _ in range(2):
        alloc_trace.append({"Entity_ID": 201, "Op": "ALLOC", "Size": 512})

    # Target Entities to pass to Turn 3 should be 103 and 105.

    with open("memory_dumps/alloc_trace.json", "w", encoding="utf-8") as f:
        json.dump(alloc_trace, f, indent=2)

def build_turn_3():
    os.makedirs("engine_configs", exist_ok=True)
    
    yaml_content = """# Solver overrides for hotfix
Layer_Destructible:
  positional_iters: 4
  velocity_iters: 1
Layer_Vehicle:
  positional_iters: 8
  velocity_iters: 2
Layer_Water:
  positional_iters: 2
  velocity_iters: 1
Layer_Invisible:
  positional_iters: 1
  velocity_iters: 1
"""
    with open("engine_configs/solver_overrides.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_content)

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
