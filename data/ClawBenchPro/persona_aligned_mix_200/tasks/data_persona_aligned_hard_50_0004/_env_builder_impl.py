import os
import json
import random

def build_env():
    # 1. 建立极其碎片的废土目录树
    dirs = [
        "sys_config",
        "calibration",
        "vehicle_logs/can_bus",
        "vehicle_logs/vision_frames/camera_front",
        "vehicle_logs/vision_frames/camera_rear",
        "vehicle_logs/vision_frames/lidar_fused"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. 生成多跳推理的关键线索文件 (噪音与真相混杂)
    
    # 配置文件：埋藏不同路况的阈值，让 Agent 推理出 'highway'
    safety_params = {
        "metadata": {"version": "1.4.2", "last_updated": "2023-11-20"},
        "active_profiles_doc": "See testing schedule for current profile",
        "profiles": {
            "urban": {"min_confidence": 0.85, "max_time_drift_ms": 30},
            "highway": {"min_confidence": 0.65, "max_time_drift_ms": 50},  # <--- 真相
            "parking": {"min_confidence": 0.50, "max_time_drift_ms": 100}
        }
    }
    with open("sys_config/safety_params.json", "w") as f:
        json.dump(safety_params, f, indent=2)

    # DBC 映射表：隐藏雷达的真实 CAN ID
    fake_dbc_lines = [f"ID_SENSOR_{i}=0x{random.randint(100, 200):03X}" for i in range(50)]
    fake_dbc_lines.append("FRONT_RADAR_OBJ=0x1B3")  # <--- 真相 ID
    fake_dbc_lines += [f"ID_DEBUG_{i}=0x{random.randint(300, 400):03X}" for i in range(50)]
    random.shuffle(fake_dbc_lines)
    with open("sys_config/dbc_mapping.txt", "w") as f:
        f.write("# CONFIDENTIAL DBC MAPPING\n")
        f.write("\n".join(fake_dbc_lines))

    # 3. 生成核心测试数据 (规模化 + 随机漂移)
    objects = []
    base_time_s = 1715000000.000
    
    # 设定 120 个物体，制造特定数量的幽灵障碍物
    for i in range(1, 121):
        obj_id = i
        can_ts = base_time_s + (i * 0.15)
        
        # 随机决定当前物体的命运
        destiny = random.random()
        is_ghost = False
        
        if destiny < 0.15: 
            # 幽灵：时间戳漂移过大 ( > 50ms )
            drift = random.choice([0.060, 0.080, -0.065, -0.090])
            vis_ts_ms = int(round((can_ts + drift) * 1000))
            conf = random.uniform(0.70, 0.99)
            is_ghost = True
        elif destiny < 0.30:
            # 幽灵：置信度过低 ( < 0.65 )
            drift = random.choice([0.010, -0.015, 0.020])
            vis_ts_ms = int(round((can_ts + drift) * 1000))
            conf = random.uniform(0.15, 0.60)
            is_ghost = True
        elif destiny < 0.40:
            # 幽灵：双重违规
            drift = 0.075
            vis_ts_ms = int(round((can_ts + drift) * 1000))
            conf = 0.45
            is_ghost = True
        else:
            # 正常目标
            drift = random.choice([0.010, -0.020, 0.035, -0.040, 0.005])
            vis_ts_ms = int(round((can_ts + drift) * 1000))
            conf = random.uniform(0.68, 0.99)
            
        objects.append({
            "id": obj_id,
            "hex_id": f"{obj_id:02X}",
            "can_ts": can_ts,
            "vis_ts_ms": vis_ts_ms,
            "conf": conf
        })

    # 4. 生成海量 CAN 日志碎片
    all_can_logs = []
    
    # 混入 120 条真实的雷达报文
    for obj in objects:
        payload = f"{obj['hex_id']} " + " ".join([f"{random.randint(0, 255):02X}" for _ in range(7)])
        all_can_logs.append(f"[{obj['can_ts']:.3f}] can1 RX - - 1B3 [8] {payload}")
        
    # 强行混入 8000 条噪音 CAN 报文
    for _ in range(8000):
        noise_ts = base_time_s + random.uniform(0, 20)
        noise_id = random.choice(["0A2", "1C4", "222", "1B4", "0FF"]) # 包含曾经的0A2作为诱饵
        payload = " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)])
        all_can_logs.append(f"[{noise_ts:.3f}] can1 RX - - {noise_id} [8] {payload}")
        
    all_can_logs.sort(key=lambda x: float(x.split("]")[0][1:]))
    
    # 将日志切分为 25 个碎片文件
    chunk_size = len(all_can_logs) // 25
    for i in range(25):
        start = i * chunk_size
        end = len(all_can_logs) if i == 24 else (i + 1) * chunk_size
        with open(f"vehicle_logs/can_bus/trace_part_{i:02d}.log", "w") as f:
            f.write("\n".join(all_can_logs[start:end]) + "\n")

    # 5. 生成极度破碎的视觉单帧 JSON
    def create_vision_json(obj_id, ts_ms, conf, status, sensor):
        return {
            "metadata": {
                "frame_status": status,
                "sensor": sensor,
                "sync_mode": "loose"
            },
            "frame_info": {
                "system_timestamp_ms": ts_ms,
            },
            "detected_entities": [
                {
                    "entity_id": obj_id,
                    "metrics": {
                        "confidence_score": conf,
                        "occlusion_ratio": random.uniform(0, 0.2)
                    },
                    "bounding_box": {
                        "x": random.uniform(10, 50),
                        "y": random.uniform(-5, 5),
                        "z": random.uniform(-1, 2)
                    }
                }
            ]
        }

    # 真实的有效前向帧
    for obj in objects:
        data = create_vision_json(obj["id"], obj["vis_ts_ms"], obj["conf"], "VALID", "front_center_camera")
        with open(f"vehicle_logs/vision_frames/camera_front/frame_{obj['id']:04d}.json", "w") as f:
            json.dump(data, f, indent=2)

    # 制造损坏的前向帧 (诱饵：时间戳或置信度异常，但状态是CORRUPTED，应被过滤)
    for i in range(200, 250):
        data = create_vision_json(i, int((base_time_s + i) * 1000), 0.1, "CORRUPTED", "front_center_camera")
        with open(f"vehicle_logs/vision_frames/camera_front/dump_err_{i:04d}.json", "w") as f:
            json.dump(data, f)

    # 制造后视摄像头的有效帧 (诱饵：状态有效，但是不相关的摄像头，应被过滤)
    for i in range(1, 60):
        data = create_vision_json(i, int((base_time_s + i) * 1000), 0.9, "VALID", "rear_camera")
        with open(f"vehicle_logs/vision_frames/camera_rear/frame_{i:04d}.json", "w") as f:
            json.dump(data, f)

    # 制造Lidar雷达诱饵目录
    for i in range(300, 310):
        with open(f"vehicle_logs/vision_frames/lidar_fused/cloud_{i}.json", "w") as f:
            json.dump({"status": "OFFLINE"}, f)
