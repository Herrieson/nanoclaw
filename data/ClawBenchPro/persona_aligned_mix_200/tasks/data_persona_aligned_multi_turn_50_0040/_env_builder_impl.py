import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("profiling", exist_ok=True)
    os.makedirs("memory/heaps", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    # 1. 构造 ECS Profiling Log
    # 陷阱：Frame 15 掉帧，但原因是 AI 逻辑（npc_boss_01），内存连续
    # 真实目标：Frame 32 掉帧，obj_barrel_01 和 obj_debris_05 耗时高，包含 PhysicsBody 且内存碎片化
    log_content = """[Frame 01] DeltaTime: 12.1ms
  Entity: player_01 | Prefab: PlayerCharacter | Components: Transform, PhysicsBody, PlayerInput | Duration: 2.1ms | MemPtr: 0x1A00
  Entity: obj_barrel_01 | Prefab: ExplosiveBarrel | Components: Transform, PhysicsBody | Duration: 1.5ms | MemPtr: 0x1B01
[Frame 15] DeltaTime: 22.4ms
  Entity: npc_boss_01 | Prefab: BossMonster | Components: Transform, AIBehavior, Navigation | Duration: 14.2ms | MemPtr: 0x1C05
  Entity: obj_crate_02 | Prefab: WoodenCrate | Components: Transform, PhysicsBody | Duration: 2.3ms | MemPtr: 0x1D02
[Frame 32] DeltaTime: 18.7ms
  Entity: obj_barrel_01 | Prefab: ExplosiveBarrel | Components: Transform, PhysicsBody | Duration: 6.8ms | MemPtr: 0x1B01
  Entity: obj_debris_05 | Prefab: ConcreteDebris | Components: Transform, PhysicsBody | Duration: 5.4ms | MemPtr: 0x1E09
  Entity: player_01 | Prefab: PlayerCharacter | Components: Transform, PhysicsBody, PlayerInput | Duration: 2.2ms | MemPtr: 0x1A00
[Frame 45] DeltaTime: 15.8ms
  Entity: obj_vehicle_01 | Prefab: ArmoredCar | Components: Transform, PhysicsBody, VehicleController | Duration: 4.1ms | MemPtr: 0x1F11
"""
    with open("profiling/ecs_ticks.log", "w") as f:
        f.write(log_content)

    # 2. 构造 Memory Pool JSON
    memory_data = {
        "0x1A00": {"size": 2048, "status": "CONTIGUOUS", "cache_misses": 10},
        "0x1B01": {"size": 512, "status": "FRAGMENTED", "cache_misses": 850},  # 目标1: 碎片化
        "0x1C05": {"size": 4096, "status": "CONTIGUOUS", "cache_misses": 5},   # 干扰项: 内存连续，非物理
        "0x1D02": {"size": 512, "status": "CONTIGUOUS", "cache_misses": 20},
        "0x1E09": {"size": 256, "status": "FRAGMENTED", "cache_misses": 620},  # 目标2: 碎片化
        "0x1F11": {"size": 1024, "status": "CONTIGUOUS", "cache_misses": 45}
    }
    with open("memory/heaps/physics_pool.json", "w") as f:
        json.dump(memory_data, f, indent=2)

def build_turn_2():
    os.makedirs("console_dumps", exist_ok=True)
    # 1. 构造 Console Profiling Log
    # 之前在 PC 端 Frame 15 中勉强过关 (2.3ms) 的 obj_crate_02，在主机上 Frame 10 直接飙升导致掉帧
    # 之前 PC 上掉帧的 ExplosiveBarrel 在这里依然掉帧，但 Prompt 要求排除
    console_log_content = """[Frame 05] DeltaTime: 14.2ms
  Entity: player_01 | Prefab: PlayerCharacter | Components: Transform, PhysicsBody, PlayerInput | Duration: 3.1ms | MemPtr: 0x1A00
[Frame 10] DeltaTime: 19.5ms
  Entity: obj_crate_02 | Prefab: WoodenCrate | Components: Transform, PhysicsBody | Duration: 8.9ms | MemPtr: 0x1D02
  Entity: obj_wall_01 | Prefab: DestructibleWall | Components: Transform, Destructible | Duration: 4.1ms | MemPtr: 0x2A11
[Frame 22] DeltaTime: 20.1ms
  Entity: obj_barrel_01 | Prefab: ExplosiveBarrel | Components: Transform, PhysicsBody | Duration: 9.8ms | MemPtr: 0x1B01
  Entity: obj_crate_03 | Prefab: WoodenCrate | Components: Transform, PhysicsBody | Duration: 7.2ms | MemPtr: 0x1D03
"""
    with open("console_dumps/console_perf.log", "w") as f:
        f.write(console_log_content)

def build_turn_3():
    os.makedirs("physics", exist_ok=True)
    
    # 1. 构造 Collision Matrix CSV
    # 初始全为 1 (开启)
    matrix_data = [
        ["EntityA", "EntityB", "CollisionEnabled"],
        ["ExplosiveBarrel", "PlayerCharacter", "1"],
        ["ExplosiveBarrel", "EnvironmentGeometry", "1"],
        ["ExplosiveBarrel", "ConcreteDebris", "1"],
        ["ConcreteDebris", "PlayerCharacter", "1"],
        ["ConcreteDebris", "EnvironmentGeometry", "1"],
        ["ConcreteDebris", "BossMonster", "1"],
        ["WoodenCrate", "PlayerCharacter", "1"],
        ["WoodenCrate", "EnvironmentGeometry", "1"],
        ["WoodenCrate", "ExplosiveBarrel", "1"],
        ["ArmoredCar", "PlayerCharacter", "1"]
    ]
    with open("physics/collision_matrix.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(matrix_data)
        
    # 2. 构造 Manifest JSON
    manifest_data = {
        "PlayerCharacter": {"category": "Character", "is_critical": True},
        "BossMonster": {"category": "Character", "is_critical": True},
        "EnvironmentGeometry": {"category": "Static", "is_critical": True},
        "ExplosiveBarrel": {"category": "DynamicProp", "is_critical": False},
        "ConcreteDebris": {"category": "ParticleProp", "is_critical": False},
        "WoodenCrate": {"category": "DynamicProp", "is_critical": False},
        "ArmoredCar": {"category": "Vehicle", "is_critical": False}
    }
    with open("physics/manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=2)

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
