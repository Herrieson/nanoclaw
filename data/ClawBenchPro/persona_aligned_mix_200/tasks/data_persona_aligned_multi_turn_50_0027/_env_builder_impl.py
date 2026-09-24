import os
import argparse
import json
import random

def build_turn_1():
    os.makedirs("logs", exist_ok=True)
    
    racks = ["rack_A", "rack_B", "rack_C", "rack_D", "rack_E", "rack_F"]
    
    # 设定:
    # 正常结束时间步 = 150
    # Rank 10: mem leak at step 120 (on rack_A)
    # 死锁: 42 -> 55, 55 -> 89, 89 -> 42. (死锁发生于 step 132)
    # Ranks on racks: 
    # 42 on node_42 (rack_B)
    # 55 on node_55 (rack_C)
    # 89 on node_89 (rack_D)
    
    for rank in range(100):
        rack = racks[rank % len(racks)]
        # 硬编码死锁相关的 rack，确保后续黑名单过滤逻辑清晰
        if rank == 42: rack = "rack_B"
        if rank == 55: rack = "rack_C"
        if rank == 89: rack = "rack_D"
        if rank == 10: rack = "rack_A"
            
        hostname = f"node_c{rank:03d}_{rack}"
        filepath = os.path.join("logs", f"rank_{rank:03d}.log")
        
        with open(filepath, "w") as f:
            f.write(f"[Init] Rank {rank:03d} started on physical node {hostname}\n")
            
            if rank == 10:
                for step in range(0, 120, 10):
                    f.write(f"[Step {step}] Computation boundaries exchanged.\n")
                f.write(f"[Step 120] Critical error: Segmentation fault (core dumped). Connection lost.\n")
            
            elif rank in [42, 55, 89]:
                for step in range(0, 130, 10):
                    f.write(f"[Step {step}] Computation boundaries exchanged.\n")
                f.write(f"[Step 130] Computation boundaries exchanged.\n")
                f.write(f"[Step 131] Computation boundaries exchanged.\n")
                
                if rank == 42:
                    f.write(f"[Step 132] Blocked: Waiting for MPI_Recv from rank 055...\n")
                elif rank == 55:
                    f.write(f"[Step 132] Blocked: Waiting for MPI_Recv from rank 089...\n")
                elif rank == 89:
                    f.write(f"[Step 132] Blocked: Waiting for MPI_Recv from rank 042...\n")
                    
            else:
                # 正常节点但因为死锁卡住，未完成 150 步，停留在不同时间步，但没有明确说等某个人
                stop_step = 132
                for step in range(0, stop_step, 10):
                    f.write(f"[Step {step}] Computation boundaries exchanged.\n")
                f.write(f"[Step 130] Computation boundaries exchanged.\n")
                f.write(f"[Step 131] Computation boundaries exchanged.\n")
                f.write(f"[Step 132] Waiting for global synchronization barrier...\n")

def build_turn_2():
    # 死锁是 Step 132，发生死锁前的一个完整安全时间步应该是 Step 131。
    os.makedirs("climate_data", exist_ok=True)
    
    steps = [130, 131, 132]
    
    for step in steps:
        data = {}
        for rank in range(100):
            # 基准温度 15.0，随机扰动
            temp_grid = [
                [15.0 + random.uniform(-1, 1), 15.5 + random.uniform(-1, 1)],
                [14.8 + random.uniform(-1, 1), 16.2 + random.uniform(-1, 1)]
            ]
            wind_grid = [
                [5.0, 5.5],
                [4.8, 6.2]
            ]
            
            # Step 131 设定的异常逻辑：
            if step == 131:
                # 给rank 020 注入一个明显低于绝对零度的脏数据，它需要被整体抛弃
                if rank == 20:
                    temp_grid[0][1] = -300.0
                # 给 rank 042 注入点奇怪数据，虽然它应该被按黑名单丢弃，但如果Agent没过滤黑名单就会错
                if rank == 42:
                    temp_grid[1][1] = 999.9 
            
            # 模拟 step 132 部分节点未产出数据
            if step == 132 and rank in [42, 55, 89]:
                continue
                
            data[f"rank_{rank:03d}"] = {
                "temperature": temp_grid,
                "wind_speed": wind_grid
            }
            
        with open(os.path.join("climate_data", f"grid_step_{step}.json"), "w") as f:
            json.dump(data, f, indent=2)

def build_turn_3():
    # 坏机柜：rack_B, rack_C, rack_D (根据 rank 42, 55, 89 的分配)
    # 可用机柜：rack_A, rack_E, rack_F, rack_G
    
    cluster_status = {
        "rack_A": [
            {"hostname": "node_new_a1", "cores": 8},
            {"hostname": "node_new_a2", "cores": 8}
        ],
        "rack_B": [  # 被拉黑的机柜
            {"hostname": "node_new_b1", "cores": 16},
            {"hostname": "node_new_b2", "cores": 16}
        ],
        "rack_C": [  # 被拉黑的机柜
            {"hostname": "node_new_c1", "cores": 32}
        ],
        "rack_D": [  # 被拉黑的机柜
            {"hostname": "node_new_d1", "cores": 8}
        ],
        "rack_E": [
            {"hostname": "node_new_e1", "cores": 12},
            {"hostname": "node_new_e2", "cores": 12}
        ],
        "rack_F": [
            {"hostname": "node_new_f1", "cores": 4}
        ]
    }
    
    with open("cluster_status.json", "w") as f:
        json.dump(cluster_status, f, indent=2)

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
