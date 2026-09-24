import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("calibration", exist_ok=True)
    os.makedirs("test_run_A", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 埋点：给后续轮次设下的隐式依赖与物理状态流转基石
    specs_content = """SENSOR FUSION CALIBRATION SPECS
-------------------------------
1. Time Synchronization:
   The Chassis CAN bus hardware clock is exactly 1250 ms AHEAD of the Radar/Vision true clock.
   Formula: True_Timestamp = CAN_Timestamp - 1250 = Radar_Timestamp
   
2. CAN Hex Format (5 Bytes / 10 hex characters, e.g., 01F4000000):
   - Bytes 0-1 (uint16 big-endian): Vehicle Speed. Multiply integer value by 0.1 to get km/h.
   - Bytes 2-3 (int16 big-endian): Steering wheel angle.
   - Byte 4 (uint8): Status flag. (0x00 means normal).

3. Radar Ghost Filtering:
   Any radar target with 'confidence' < 80 is considered a "Ghost" and must be dropped.
"""
    with open("calibration/specs.txt", "w") as f:
        f.write(specs_content)

    # Turn 1 CAN 数据 (时钟快了1250)
    # 真实时间: 10000 -> CAN: 11250. 速度: 50.0km/h -> 500 -> 0x01F4
    can_data = [
        {"timestamp": 11250, "hex_data": "01F4000000"},
        {"timestamp": 11350, "hex_data": "01F4000000"},
        {"timestamp": 11450, "hex_data": "01F4000000"}
    ]
    with open("test_run_A/can.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "hex_data"])
        writer.writeheader()
        writer.writerows(can_data)

    # Turn 1 Radar 数据 (真实时间)
    radar_data = {
        "10000": [
            {"id": "obj_A", "x": 5.0, "y": 20.0, "confidence": 90},
            {"id": "obj_ghost", "x": 1.0, "y": 5.0, "confidence": 50}
        ],
        "10100": [
            {"id": "obj_A", "x": 5.0, "y": 19.5, "confidence": 91}
        ],
        "10200": [
            {"id": "obj_A", "x": 5.0, "y": 19.0, "confidence": 92},
            {"id": "obj_B", "x": -2.0, "y": 15.0, "confidence": 85}
        ]
    }
    with open("test_run_A/radar.json", "w") as f:
        json.dump(radar_data, f, indent=2)

def build_turn_2():
    os.makedirs("test_run_B", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Turn 2 CAN 数据
    # 真实时间 20000 -> CAN: 21250
    can_data = [
        {"timestamp": 21250, "hex_data": "01F4000000"}, # 50.0km/h
        {"timestamp": 21350, "hex_data": "02580000EE"}, # 60.0km/h, 但 flag 是 EE (损坏)
        {"timestamp": 21450, "hex_data": "01F4000000"}  # 50.0km/h
    ]
    with open("test_run_B/can.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "hex_data"])
        writer.writeheader()
        writer.writerows(can_data)

    # Turn 2 Radar 数据
    # 巧妙设计：obj_A 在昨天的最后一次坐标是 (5.0, 19.0)。今天在 (4.5, 19.5)。
    # 距离 = sqrt(0.5^2 + 0.5^2) = sqrt(0.5) = 0.707 < 1.5 米，所以是静态！
    # obj_B 在昨天是 (-2.0, 15.0)。今天在 (-2.0, 10.0)。移动了 5 米，非静态。
    radar_data = {
        "20000": [
            {"id": "obj_A", "x": 4.5, "y": 19.5, "confidence": 88},
            {"id": "obj_B", "x": -2.0, "y": 10.0, "confidence": 82}
        ],
        "20100": [
            {"id": "obj_A", "x": 4.5, "y": 19.5, "confidence": 89}
        ],
        "20200": [
            {"id": "obj_C", "x": 10.0, "y": 30.0, "confidence": 95}
        ]
    }
    with open("test_run_B/radar.json", "w") as f:
        json.dump(radar_data, f, indent=2)

def build_turn_3():
    os.makedirs("test_run_C", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Turn 3 CAN 数据
    can_data = [
        {"timestamp": 31250, "hex_data": "012C000000"}, # 真实 30000. 速度 30.0km/h (>25)
        {"timestamp": 31350, "hex_data": "012C0000EE"}, # 真实 30100. 速度 30.0km/h (损坏!)
        {"timestamp": 31450, "hex_data": "00C8000000"}, # 真实 30200. 速度 20.0km/h (太慢, <25)
        {"timestamp": 31550, "hex_data": "012C000000"}  # 真实 30300. 速度 30.0km/h (>25)
    ]
    with open("test_run_C/can.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "hex_data"])
        writer.writeheader()
        writer.writerows(can_data)

    # Turn 3 Vision 数据 (无confidence字段)
    vision_data = {
        "30000": [
            {"id": "cam_01", "x": 0.5, "y": 10.0}  # x<1.0, y in (0,12]. CAN>25. -> 触发!
        ],
        "30100": [
            {"id": "cam_02", "x": 0.2, "y": 8.0}   # 位置满足，但对应 CAN 损坏。 -> 不触发!
        ],
        "30200": [
            {"id": "cam_03", "x": 0.0, "y": 5.0}   # 位置满足，但车速只有 20。 -> 不触发!
        ],
        "30300": [
            {"id": "cam_04", "x": 1.5, "y": 10.0}, # x>=1.0，不在正前方。 -> 不触发!
            {"id": "cam_05", "x": -0.8, "y": 11.5} # x<1.0, y in (0,12]. CAN>25. -> 触发!
        ]
    }
    with open("test_run_C/vision.json", "w") as f:
        json.dump(vision_data, f, indent=2)

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
