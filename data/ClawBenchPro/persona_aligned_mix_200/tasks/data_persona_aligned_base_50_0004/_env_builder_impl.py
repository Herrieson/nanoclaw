import os
import json
import random

def build_env():
    # 创建工作目录
    os.makedirs("sensor_dumps", exist_ok=True)
    os.makedirs("calibration", exist_ok=True)

    # 预设的障碍物目标与时间戳逻辑 (CAN为秒，JSON为毫秒)
    # 幽灵条件：置信度 < 0.65 或 时间戳偏差绝对值 > 50ms
    objects = [
        # ID 12 (0x0C): 正常目标。Diff: 10ms < 50ms, Conf: 0.92 >= 0.65
        {"id": 12, "hex_id": "0C", "can_ts_s": 1715000000.115, "vision_ts_ms": 1715000000125, "conf": 0.92},
        # ID 18 (0x12): 幽灵目标。置信度过低。Diff: 5ms < 50ms, Conf: 0.45 < 0.65 -> GHOST
        {"id": 18, "hex_id": "12", "can_ts_s": 1715000000.195, "vision_ts_ms": 1715000000200, "conf": 0.45},
        # ID 27 (0x1B): 幽灵目标。时间戳漂移过大。Diff: 80ms > 50ms, Conf: 0.88 >= 0.65 -> GHOST
        {"id": 27, "hex_id": "1B", "can_ts_s": 1715000000.300, "vision_ts_ms": 1715000000380, "conf": 0.88},
        # ID 33 (0x21): 正常目标。Diff: 15ms < 50ms, Conf: 0.75 >= 0.65
        {"id": 33, "hex_id": "21", "can_ts_s": 1715000000.435, "vision_ts_ms": 1715000000450, "conf": 0.75},
        # ID 42 (0x2A): 幽灵目标。置信度低，且时间戳漂移。Diff: 80ms > 50ms, Conf: 0.50 < 0.65 -> GHOST
        {"id": 42, "hex_id": "2A", "can_ts_s": 1715000000.520, "vision_ts_ms": 1715000000600, "conf": 0.50},
        # ID 55 (0x37): 正常目标。临界值测试。Diff: 50ms，Conf: 0.65 -> 正常
        {"id": 55, "hex_id": "37", "can_ts_s": 1715000000.600, "vision_ts_ms": 1715000000650, "conf": 0.65},
        # ID 68 (0x44): 幽灵目标。时间戳漂移临界。Diff: 51ms > 50ms, Conf: 0.90 -> GHOST
        {"id": 68, "hex_id": "44", "can_ts_s": 1715000000.700, "vision_ts_ms": 1715000000751, "conf": 0.90},
    ]

    # 生成包含噪音的 CAN 日志
    can_logs = []
    base_time = 1715000000.000
    for _ in range(50):
        # 随机噪音 CAN 报文
        noise_ts = base_time + random.uniform(0.01, 0.99)
        noise_id = random.choice(["0B4", "1A2", "0C1", "111"])
        payload = " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)])
        can_logs.append(f"[{noise_ts:.3f}] can1 RX - - {noise_id} [8] {payload}")
    
    # 混入真实的雷达 CAN 报文 (ID 0A2)
    for obj in objects:
        payload = f"{obj['hex_id']} " + " ".join([f"{random.randint(0, 255):02X}" for _ in range(7)])
        can_logs.append(f"[{obj['can_ts_s']:.3f}] can1 RX - - 0A2 [8] {payload}")
    
    # 按时间戳排序 CAN 报文，模拟真实流
    can_logs.sort(key=lambda x: float(x.split("]")[0][1:]))

    with open("sensor_dumps/bus_trace.log", "w", encoding="utf-8") as f:
        f.write("=== VEHICLE DATABUS DUMP v2.1 ===\n")
        f.write("INTERFACE: can1\n")
        f.write("\n".join(can_logs) + "\n")

    # 生成嵌套极深的视觉 JSON
    fusion_frames = []
    for obj in objects:
        frame_data = {
            "metadata": {
                "sync_mode": "loose",
                "calib_status": "OK"
            },
            "frame_info": {
                "system_timestamp_ms": obj["vision_ts_ms"],
                "processing_latency_ms": random.randint(10, 30)
            },
            "sensors": {
                "front_center_camera": {
                    "detected_entities": [
                        {
                            "entity_id": obj["id"],
                            "metrics": {
                                "confidence_score": obj["conf"],
                                "occlusion_ratio": random.uniform(0, 0.2)
                            },
                            "bounding_box": {
                                "x": random.uniform(10, 50),
                                "y": random.uniform(-5, 5),
                                "z": random.uniform(-1, 2)
                            }
                        }
                    ]
                },
                # 干扰项
                "rear_camera": {
                    "detected_entities": []
                }
            }
        }
        fusion_frames.append(frame_data)
        
        # 随机插入空帧作为干扰
        if random.random() > 0.7:
             empty_frame = {
                 "frame_info": {"system_timestamp_ms": obj["vision_ts_ms"] + 5},
                 "sensors": {"front_center_camera": {"detected_entities": []}}
             }
             fusion_frames.append(empty_frame)

    vision_data = {
        "export_version": "v3.1.4-rc2",
        "session_id": "ROADTEST-2023-11-20",
        "payload": {
            "fusion_stream": fusion_frames
        }
    }

    with open("sensor_dumps/vision_fusion.json", "w", encoding="utf-8") as f:
        json.dump(vision_data, f, indent=2)
