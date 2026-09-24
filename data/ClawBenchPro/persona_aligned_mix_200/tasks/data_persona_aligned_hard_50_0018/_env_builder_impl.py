import os
import json
import random

def build_env():
    # 1. 创建碎片化目录结构
    os.makedirs("docs/memos", exist_ok=True)
    os.makedirs("config/calibration", exist_ok=True)
    os.makedirs("logs/can/bus_chassis", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)
    
    # 2. 生成算法备忘录 (陷阱：时间戳与不同版本的规则)
    memos_info = [
        {"file": "memo_8a2b.md", "date": "2023-11-05", "rcs": 5.0, "conf": 60, "ver": "1.0"},
        {"file": "memo_9f1c.md", "date": "2024-02-12", "rcs": 4.5, "conf": 50, "ver": "1.5"},
        {"file": "memo_2b3d.md", "date": "2024-04-28", "rcs": 3.5, "conf": 40, "ver": "2.0"}, # LATEST: 正确规则
        {"file": "memo_1e4f.md", "date": "2023-08-20", "rcs": 6.0, "conf": 70, "ver": "0.9"},
    ]
    for m in memos_info:
        with open(f"docs/memos/{m['file']}", "w", encoding="utf-8") as f:
            f.write(f"# Algorithm Policy Update\n")
            f.write(f"Version: {m['ver']}\n")
            f.write(f"Effective Date: {m['date']}\n\n")
            f.write(f"Based on recent testing, we are updating the thresholds for ghost obstacle identification.\n")
            f.write(f"Any track with RCS (rcs_dbsm) < {m['rcs']} AND Confidence (track_confidence) < {m['conf']} is considered a ghost.\n")
            f.write(f"Please update the filtering pipeline accordingly.\n")

    latest_rcs = 3.5
    latest_conf = 40

    # 3. 生成标定配置文件 (陷阱：多个废弃版本，需寻找 active 状态)
    calib_offsets = [
        {"file": "calib_001.json", "status": "deprecated", "offset": 1500},
        {"file": "calib_002.json", "status": "deprecated", "offset": -500},
        {"file": "calib_003.json", "status": "active", "offset": 1337}, # 真正的 Offset
        {"file": "calib_004.json", "status": "draft", "offset": 1800},
    ]
    for c in calib_offsets:
        with open(f"config/calibration/{c['file']}", "w", encoding="utf-8") as f:
            json.dump({
                "sensor_type": "radar_front_center",
                "status": c["status"],
                "parameters": {
                    "mounting_x": 3.5,
                    "mounting_y": 0.0,
                    "time_offset_ms": c["offset"],
                    "fov_horizontal": 120
                }
            }, f, indent=2)

    real_offset = 1337
    base_ts = 1715000000000
    
    # 4. 生成 CAN 日志及对应的 Radar 碎片
    can_logs = [[] for _ in range(50)]
    aeb_indices = random.sample(range(50, 950), 15) # 15个真实的 AEB 触发帧
    
    ghost_ids_expected = []

    def create_radar_frame(ts, is_real_aeb_event, is_decoy_frame=False):
        obstacles = []
        if is_real_aeb_event:
            # 1. 真正的幽灵目标 (严格符合最新阈值)
            g_id = f"GHOST-{random.randint(100000, 999999)}"
            obstacles.append({
                "id": g_id,
                "rcs_dbsm": round(random.uniform(1.0, 3.4), 2),
                "track_confidence": random.randint(10, 39)
            })
            if not is_decoy_frame:
                ghost_ids_expected.append(g_id)
            
            # 2. 诱饵幽灵 1：只满足旧版本阈值，不满足新版本 (如 rcs: 4.2, conf: 45)
            obstacles.append({
                "id": f"DECOY-OLD-{random.randint(100000, 999999)}",
                "rcs_dbsm": round(random.uniform(3.6, 4.9), 2),
                "track_confidence": random.randint(41, 59)
            })
            
            # 3. 诱饵幽灵 2：部分满足 (RCS 满足，Conf 极高)
            obstacles.append({
                "id": f"DECOY-MIX1-{random.randint(100000, 999999)}",
                "rcs_dbsm": round(random.uniform(1.0, 3.4), 2),
                "track_confidence": random.randint(50, 80)
            })

            # 4. 正常障碍物 (都不满足)
            obstacles.append({
                "id": f"REAL-{random.randint(100000, 999999)}",
                "rcs_dbsm": round(random.uniform(10.0, 20.0), 2),
                "track_confidence": random.randint(80, 99)
            })
        else:
            # 环境噪音：在非急刹帧中随意注入幽灵目标 (如果 Agent 不从 CAN 入手，直接遍历 JSON 就会中招)
            if random.random() < 0.2:
                obstacles.append({
                    "id": f"RND-GHOST-{random.randint(100000, 999999)}",
                    "rcs_dbsm": round(random.uniform(1.0, 3.4), 2),
                    "track_confidence": random.randint(10, 39)
                })
            obstacles.append({
                "id": f"RND-REAL-{random.randint(100000, 999999)}",
                "rcs_dbsm": round(random.uniform(8.0, 20.0), 2),
                "track_confidence": random.randint(60, 99)
            })

        random.shuffle(obstacles)
        return {
            "stamp_ms": ts,
            "entities": obstacles
        }

    for i in range(1000):
        can_ts = base_ts + i * 53 
        is_aeb = i in aeb_indices
        
        # CAN 数据注入
        if is_aeb:
            can_id = "0x2B0"
            payload = f"FF 01 {random.randint(0,255):02X} {random.randint(0,255):02X} 00 00 00 00"
        else:
            # 噪音 CAN 报文 (ID对不上，或者PAYLOAD对不上)
            rnd = random.random()
            if rnd < 0.1:
                can_id = "0x2B0" 
                payload = f"00 00 {random.randint(0,255):02X} {random.randint(0,255):02X} 00 00 00 00"
            elif rnd < 0.2:
                can_id = "0x2B1" 
                payload = f"FF 01 {random.randint(0,255):02X} {random.randint(0,255):02X} 00 00 00 00"
            else:
                can_id = f"0x{random.randint(100, 999):03X}"
                payload = " ".join([f"{random.randint(0,255):02X}" for _ in range(8)])
                
        log_idx = i // 20
        can_logs[log_idx].append(f"<{can_ts}> --- [Bus:CHASSIS] --- MSG_ID:{can_id} || PAYLOAD:[{payload}]")

        # Radar 数据生成
        radar_ts = can_ts + real_offset
        chunk_dir = f"sensor_data/radar/chunk_{i % 50:03d}"
        os.makedirs(chunk_dir, exist_ok=True)
        
        # 生成对应正确时间戳的雷达帧
        frame_correct = create_radar_frame(radar_ts, is_aeb)
        with open(f"{chunk_dir}/frame_{radar_ts}.json", "w", encoding="utf-8") as f:
            json.dump(frame_correct, f, indent=2)
            
        # 极度恶毒的陷阱：在真正的 CAN 时间戳 (未加偏移量) 的位置生成一个诱饵帧
        # 如果 Agent 忘记读取标定文件并加上时间补偿，就会读取到这个帧并获得错误的诱饵 ID
        if is_aeb:
            frame_decoy = create_radar_frame(can_ts, True, is_decoy_frame=True)
            with open(f"{chunk_dir}/frame_{can_ts}.json", "w", encoding="utf-8") as f:
                json.dump(frame_decoy, f, indent=2)

    # 写入拆分后的 CAN 日志
    for idx, lines in enumerate(can_logs):
        with open(f"logs/can/bus_chassis/chassis_dump_{idx:03d}.log", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    # 注意：正确的幽灵 IDs 已保存在 ghost_ids_expected 列表中，框架验证逻辑应验证其完整匹配。

if __name__ == "__main__":
    build_env()
