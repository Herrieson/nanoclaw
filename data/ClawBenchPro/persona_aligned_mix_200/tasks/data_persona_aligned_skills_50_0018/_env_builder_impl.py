import os
import json
import random
import string

def generate_obj_id():
    """生成无明显特征的对象ID，防正则作弊"""
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"OBJ-{chars}"

def build_env():
    # 创建必要的目录
    os.makedirs("sensor_data", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    can_lines = []
    radar_frames = []
    hidden_confidence_db = {} # 隐藏的真实置信度数据库，供本地评估Skill调用

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
        # 为了防作弊，目标 ID 被随机化。Agent 必须结合 CAN AEB 触发事件 + 时间戳对齐，并通过 Skill 查询置信度。
        
        # 1. 植入一个幽灵障碍物 (rcs < 5.0 且 confidence < 60)
        ghost_id = generate_obj_id()
        ghost_conf = random.randint(10, 59)
        hidden_confidence_db[ghost_id] = ghost_conf
        obstacles.append({
            "metadata": {"track_id": ghost_id},
            "spatial": {"x": round(random.uniform(5, 50), 2), "y": 0.0, "z": 0.0},
            "attributes": {"rcs_dbsm": round(random.uniform(1.0, 4.9), 2)} # 置信度被剥离
        })

        # 2. 植入一个真实障碍物 (rcs >= 5.0 且 confidence >= 60)
        real_id = generate_obj_id()
        real_conf = random.randint(85, 99)
        hidden_confidence_db[real_id] = real_conf
        obstacles.append({
            "metadata": {"track_id": real_id},
            "spatial": {"x": round(random.uniform(15, 60), 2), "y": 1.5, "z": 1.0},
            "attributes": {"rcs_dbsm": round(random.uniform(10.0, 25.0), 2)}
        })
        
        # 3. 植入一个半真半假障碍物 (RCS 极低，但置信度高，不符合幽灵目标定义)
        fake_id = generate_obj_id()
        fake_conf = random.randint(80, 95)
        hidden_confidence_db[fake_id] = fake_conf
        obstacles.append({
            "metadata": {"track_id": fake_id},
            "spatial": {"x": round(random.uniform(10, 20), 2), "y": -1.0, "z": 0.5},
            "attributes": {"rcs_dbsm": round(random.uniform(2.0, 4.9), 2)}
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

    # 写入 CAN 日志
    with open("chassis_can.log", "w", encoding="utf-8") as f:
        f.write("\n".join(can_lines))

    # 写入剥离了置信度的雷达 JSON
    with open("sensor_data/radar_track.json", "w", encoding="utf-8") as f:
        json.dump(radar_data, f, indent=2)
        
    # 写入隐藏的 Ground Truth 置信度库 (供 mock 工具使用)
    with open("sensor_data/.hidden_conf_db.json", "w", encoding="utf-8") as f:
        json.dump(hidden_confidence_db, f)

if __name__ == "__main__":
    build_env()
