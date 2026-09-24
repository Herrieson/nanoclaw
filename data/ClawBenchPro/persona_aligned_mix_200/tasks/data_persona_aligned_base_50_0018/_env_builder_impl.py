import os
import json
import random

def build_env():
    # 创建必要的目录
    os.makedirs("sensor_data", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    can_lines = []
    radar_frames = []

    # 设定一个基础时间戳 (UNIX 毫秒级别)
    base_ts = 1715000000000
    
    # 随机选定几个时刻作为真正的 AEB 触发帧
    aeb_indices = [23, 77, 142, 189]

    for i in range(200):
        # 底盘 CAN 时间戳
        can_ts = base_ts + i * 50
        # 雷达时间快 1500ms
        radar_ts = can_ts + 1500

        obstacles = []
        is_aeb = i in aeb_indices

        # ================= CAN 数据生成 =================
        if is_aeb:
            can_id = "0x2B0"
            # FF 01 代表刹车触发
            data = f"FF 01 {random.randint(0, 255):02X} {random.randint(0, 255):02X} 00 00 00 00"
        else:
            # 加入强干扰项：相同的 CAN ID，但 PAYLOAD 不是 FF 01 (即未触发刹车)
            if random.random() < 0.15:
                can_id = "0x2B0"
                data = f"00 00 {random.randint(0, 255):02X} {random.randint(0, 255):02X} 00 00 00 00"
            else:
                can_id = random.choice(["0x1A0", "0x3C1", "0x405"])
                data = " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)])

        # 构造带有乱码感和非标准分隔符的底盘日志
        can_lines.append(f"<{can_ts}> --- [Bus:CHASSIS] --- MSG_ID:{can_id} || PAYLOAD:[{data}]")

        # ================= 雷达数据生成 =================
        # 为了防作弊，我们在非 AEB 帧和 AEB 帧中都注入 "幽灵" 属性的目标
        # Agent 必须结合 CAN AEB 触发事件 + 时间戳对齐，才能准确拿到正确的幽灵 ID
        
        # 1. 植入一个幽灵障碍物 (rcs < 5.0 且 confidence < 60)
        ghost_id = f"GHOST-{random.randint(10000, 99999)}"
        obstacles.append({
            "metadata": {"track_id": ghost_id},
            "spatial": {"x": round(random.uniform(5, 50), 2), "y": 0.0, "z": 0.0},
            "attributes": {"rcs_dbsm": round(random.uniform(1.0, 4.9), 2), "track_confidence": random.randint(10, 59)}
        })

        # 2. 植入一个真实障碍物 (rcs >= 5.0 且 confidence >= 60)
        real_id = f"REAL-{random.randint(10000, 99999)}"
        obstacles.append({
            "metadata": {"track_id": real_id},
            "spatial": {"x": round(random.uniform(15, 60), 2), "y": 1.5, "z": 1.0},
            "attributes": {"rcs_dbsm": round(random.uniform(10.0, 25.0), 2), "track_confidence": random.randint(85, 99)}
        })
        
        # 3. 植入一个半真半假障碍物 (RCS 满足，但置信度低)
        fake_id = f"FAKE-{random.randint(10000, 99999)}"
        obstacles.append({
            "metadata": {"track_id": fake_id},
            "spatial": {"x": round(random.uniform(10, 20), 2), "y": -1.0, "z": 0.5},
            "attributes": {"rcs_dbsm": round(random.uniform(6.0, 15.0), 2), "track_confidence": random.randint(20, 50)}
        })

        # 打乱当前帧的追踪对象序列
        random.shuffle(obstacles)

        # 极度深层的嵌套 JSON 结构
        radar_frames.append({
            "header": {
                "sequence": i, 
                "stamp_ms": radar_ts,
                "sensor_health": "OK"
            },
            "payload": {
                "tracked_entities": {
                    "count": len(obstacles),
                    "radar_objects": obstacles
                }
            }
        })

    # 包装最终的巨型 JSON
    radar_data = {
        "vehicle_id": "TEST_MULE_08",
        "campaign": "URBAN_NIGHT_V2",
        "data_stream": {
            "radar_front_center": {
                "hardware_rev": "D1",
                "software_version": "v1.2.4-beta",
                "frames": radar_frames
            }
        }
    }

    # 写入文件
    with open("chassis_can.log", "w", encoding="utf-8") as f:
        f.write("\n".join(can_lines))

    with open("sensor_data/radar_track.json", "w", encoding="utf-8") as f:
        json.dump(radar_data, f, indent=2)

if __name__ == "__main__":
    build_env()
