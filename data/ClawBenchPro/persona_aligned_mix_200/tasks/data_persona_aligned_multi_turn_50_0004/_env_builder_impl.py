import os
import argparse
import json
import random

def hex_format(val, length):
    return " ".join([f"{b:02X}" for b in val.to_bytes(length, byteorder='big', signed=True)])

def build_turn_1():
    os.makedirs("can_bus_logs", exist_ok=True)
    os.makedirs("sensor_fusion", exist_ok=True)
    os.makedirs("processed_data", exist_ok=True)

    can_logs = []
    radar_logs = []
    
    base_time = 1700000000000
    
    # 构造 Turn 1 数据
    for i in range(10):
        t_can = base_time + i * 100
        
        # Ego Speed: Base 50 km/h, slight variations
        ego_speed = 50.0 + i * 1.5
        speed_raw = int(ego_speed / 0.01)
        can_logs.append(f"{t_can} | 0x1A4 | {hex_format(speed_raw, 2)}")
        
        # Steering: slight turns
        steering = 2.5 * (i % 3)
        steering_raw = int(steering / 0.1)
        can_logs.append(f"{t_can + 5} | 0x2B5 | {hex_format(steering_raw, 2)}")

        # Radar Frame (Aligned closely with t_can)
        t_radar = t_can + random.randint(-20, 20)
        obstacles = []
        
        if i == 2:
            # 正常障碍物
            obstacles.append({"id": "obs_001", "confidence": 0.92, "distance": 80.5, "rel_speed_x": -20.0})
        elif i == 4:
            # 低置信度陷阱 (Conf = 0.82 < 0.85)
            obstacles.append({"id": "obs_002", "confidence": 0.82, "distance": 40.0, "rel_speed_x": -10.0})
        elif i == 6:
            # 幽灵障碍物陷阱 (Ego speed ~59, rel_speed 150 -> abs = 209 > 200)
            obstacles.append({"id": "obs_ghost", "confidence": 0.99, "distance": 15.0, "rel_speed_x": 150.0})
        elif i == 8:
            # 完美的高危障碍物 (为了第三轮的TTC < 2.0s: Ego~62, rel_speed_x = -72km/h(-20m/s), dist=30m -> TTC=1.5s)
            obstacles.append({"id": "obs_critical_1", "confidence": 0.95, "distance": 30.0, "rel_speed_x": -72.0})

        radar_logs.append({
            "timestamp": t_radar,
            "obstacles": obstacles
        })

    with open("can_bus_logs/drive_01.log", "w") as f:
        f.write("\n".join(can_logs))
        
    with open("sensor_fusion/vision_radar_01.json", "w") as f:
        json.dump(radar_logs, f, indent=2)


def build_turn_2():
    # 增量第二轮数据，模拟带 120ms 时间差和雨天CAN
    os.makedirs("can_bus_logs", exist_ok=True)
    os.makedirs("sensor_fusion", exist_ok=True)

    can_logs = []
    radar_logs = []
    
    base_time = 1700000050000
    
    for i in range(10):
        t_can = base_time + i * 100
        
        # 车速 40km/h 左右
        ego_speed = 40.0 + i * 2.0
        speed_raw = int(ego_speed / 0.01)
        can_logs.append(f"{t_can} | 0x1A4 | {hex_format(speed_raw, 2)}")
        
        # 雨天标志: 前5帧雨天(01)，后5帧晴天(00)
        is_rain = 1 if i < 5 else 0
        can_logs.append(f"{t_can + 2} | 0x3C6 | {hex_format(is_rain, 1)}")
        
        steering_raw = int(0.0 / 0.1)
        can_logs.append(f"{t_can + 5} | 0x2B5 | {hex_format(steering_raw, 2)}")

        # Radar 时间戳有 120ms 提前偏差
        t_radar = t_can + 120 + random.randint(-15, 15)
        obstacles = []
        
        if i == 3:
            # 雨天下的障碍物，置信度 0.78 (因为雨天阈值为 0.85-0.10=0.75，所以这是合规的!)
            # TTC 高危：rel_speed_x = -108km/h(-30m/s), dist = 45m -> TTC=1.5s
            obstacles.append({"id": "obs_rain_crit", "confidence": 0.78, "distance": 45.0, "rel_speed_x": -108.0})
        elif i == 7:
            # 晴天下的障碍物，置信度 0.80 (晴天阈值仍为0.85，应被剔除!)
            obstacles.append({"id": "obs_clear_fail", "confidence": 0.80, "distance": 50.0, "rel_speed_x": -20.0})
        elif i == 9:
            # 另一个幽灵陷阱: ego~58, rel_speed=-260 -> abs(-202) > 200, 剔除!
            obstacles.append({"id": "obs_ghost_2", "confidence": 0.98, "distance": 100.0, "rel_speed_x": -260.0})

        radar_logs.append({
            "timestamp": t_radar,
            "obstacles": obstacles
        })

    with open("can_bus_logs/drive_02.log", "w") as f:
        f.write("\n".join(can_logs))
        
    with open("sensor_fusion/vision_radar_02.json", "w") as f:
        json.dump(radar_logs, f, indent=2)


def build_turn_3():
    # 第三轮不新增初始文件，完全依靠Agent跨文件合并前两轮自己生成的 processed_data
    pass


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
