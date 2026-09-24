import os
import argparse
import struct
import json
import math

def generate_hex_string(data_bytes):
    # 模拟真实世界日志，加入一些噪音前缀和换行
    hex_str = data_bytes.hex().upper()
    # 每两个字符加个空格
    spaced = " ".join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])
    return f"[RAW_RECV_BUFFER] 0x{spaced}\n"

def make_packet(sync, sub_id, seq, ts, payload_bytes, force_chk=None):
    packet_id = (sub_id << 12) | (seq & 0x0FFF)
    header = struct.pack(">HHLB", sync, packet_id, ts, len(payload_bytes))
    data = header + payload_bytes
    chk = 0
    for b in data:
        chk ^= b
    if force_chk is not None:
        chk = force_chk
    return data + struct.pack("B", chk)

def make_star_tracker_payload(q1, q2, q3, q4):
    return struct.pack(">ffff", q1, q2, q3, q4)

def make_propulsion_payload(temp, pressure):
    return struct.pack(">ff", temp, pressure)

def write_log(filepath, lines):
    with open(filepath, "w") as f:
        # 加入一些垃圾行干扰
        f.write("[SYS] INIT LINK ESTABLISHED\n")
        f.write("GARBAGE DATA RECV: 00 11 22 33 44 55\n")
        for line in lines:
            f.write(line)
        f.write("[SYS] LINK LOST\n")

def build_turn_1():
    os.makedirs("docs", exist_ok=True)
    os.makedirs("downlink_logs/session_A", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    manual_content = """# 星空-7号底层遥测包解析手册 v2.1

## 1. 基础物理层帧格式
每个遥测包由十六进制流构成，包含以下字段（全部为 Big-Endian 网络字节序）：
- **SYNC WORD (2 bytes)**: 同步字，正常情况下应高字节为 `0x1A`，低字节在 `0xC0` 到 `0xCF` 之间。
- **PACKET ID (2 bytes)**:
  - Bit 15-12: Subsystem ID 子系统标识。其中 `0x3` 为星象仪(Star Tracker)，`0x5` 为动力系统(Propulsion)。
  - Bit 11-0: Sequence Number 序列号（0-4095循环）。
- **TIMESTAMP (4 bytes)**: 卫星当地时间的无符号整数时间戳 (uint32)。
- **PAYLOAD LENGTH (1 byte)**: 数据段长度(字节数)。
- **PAYLOAD (N bytes)**: 子系统具体数据。
- **CHECKSUM (1 byte)**: 从 SYNC 开始到 PAYLOAD 结束的所有字节的异或和 (XOR sum)。

## 2. 子系统 Payload 格式
### 星象仪 (Subsystem ID: 3)
- 长度: 16 bytes
- 内容: 4个 IEEE 754 float32 浮点数，依次代表姿态四元数 Q1, Q2, Q3, Q4。

### 动力系统 (Subsystem ID: 5)
- 长度: 8 bytes
- 内容: 2个 IEEE 754 float32 浮点数，依次代表 燃烧室温度(Temp) 和 舱内压力(Pressure)。

## 3. 极端环境容错恢复机制
受强辐射影响，硬件校验和可能计算错误。为尽最大可能挽救数据，对于**星象仪 (ID: 3)** 引入以下强制接收容错规则：
如果计算出的 CHECKSUM 与包尾不符，但满足以下所有条件，仍视该包为**有效包**：
1. SYNC, PACKET ID (必须是3), LENGTH (必须是16) 均符合规范。
2. 该包的时间戳，刚好等于系统记录的**上一个已确认的有效星象仪包的时间戳 + 1** 或 **+ 2**。
注意：如果是系统处理的第一个包，且校验和错误，则直接丢弃，不适用容错机制。
"""
    with open("docs/telemetry_manual_v2.md", "w") as f:
        f.write(manual_content)

    logs = []
    # 包1：正常包 TS=1000, 模长约等于1 (0.5, 0.5, 0.5, 0.5)
    p1 = make_packet(0x1AC0, 3, 1, 1000, make_star_tracker_payload(0.5, 0.5, 0.5, 0.5))
    logs.append(generate_hex_string(p1))
    
    # 干扰包：其他系统
    p_err1 = make_packet(0x1AC1, 4, 2, 1001, b'\x00\x00\x00\x00')
    logs.append(generate_hex_string(p_err1))

    # 包2：校验错包，但 TS=1001 (正好+1)，容错条件满足，应被接纳！(0.8, 0, 0.6, 0)
    p2 = make_packet(0x1ACF, 3, 3, 1001, make_star_tracker_payload(0.8, 0.0, 0.6, 0.0), force_chk=0xFF)
    logs.append(generate_hex_string(p2))

    # 包3：校验错包，TS=1005 (距离上一个有效1001跳了4)，不满足容错，应丢弃。
    p3 = make_packet(0x1ACA, 3, 4, 1005, make_star_tracker_payload(0.1, 0.1, 0.1, 0.1), force_chk=0x00)
    logs.append(generate_hex_string(p3))

    # 包4：正常包，TS=1008
    p4 = make_packet(0x1AC2, 3, 5, 1008, make_star_tracker_payload(0.4, 0.4, 0.4, 0.707106))
    logs.append(generate_hex_string(p4))

    write_log("downlink_logs/session_A/raw_telemetry_pt1.log", logs)


def build_turn_2():
    # 注意：真实测试时turn_2会在turn_1结束后复制工作区，所以turn_1留下的文件都在。
    os.makedirs("downlink_logs/session_B", exist_ok=True)
    os.makedirs("updates", exist_ok=True)

    # 动态阈值文件
    thresholds = {
        "description": "Star Tracker Attitude Norm Deviation Threshold",
        "norm_deviation_limit_abs": 0.08,
        "required_continuous_points": 3
    }
    with open("updates/thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=4)

    logs = []
    # 回顾：Turn 1 最后一个有效包是包4，TS=1008
    # 坑点：第二天一开始就来个容错包，TS=1010 (+2)。如果没记Turn1结尾，这个就丢了！
    # 如果这个丢了，就无法衔接后面的连续3个异常点，导致找错时间窗口！
    p5 = make_packet(0x1AC9, 3, 6, 1010, make_star_tracker_payload(0.5, -0.5, 0.5, 0.5), force_chk=0xAA)
    logs.append(generate_hex_string(p5))

    # 异常开始，模长明显偏离 1 (例如达到 1.15，偏差 0.15 > 0.08)
    # TS = 1011
    p6 = make_packet(0x1AC0, 3, 7, 1011, make_star_tracker_payload(1.0, 0.5, 0.0, 0.2)) # norm ≈ 1.135
    logs.append(generate_hex_string(p6))
    
    # TS = 1012
    p7 = make_packet(0x1AC0, 3, 8, 1012, make_star_tracker_payload(0.9, 0.6, 0.3, 0.1)) # norm ≈ 1.126
    logs.append(generate_hex_string(p7))

    # TS = 1013 (连续第三个点，符合要求)
    p8 = make_packet(0x1AC0, 3, 9, 1013, make_star_tracker_payload(0.8, 0.7, 0.4, 0.2)) # norm ≈ 1.153
    logs.append(generate_hex_string(p8))

    # 恢复正常 TS = 1014
    p9 = make_packet(0x1AC0, 3, 10, 1014, make_star_tracker_payload(0.5, 0.5, 0.5, 0.5))
    logs.append(generate_hex_string(p9))

    write_log("downlink_logs/session_B/raw_telemetry_pt2.log", logs)

def build_turn_3():
    os.makedirs("downlink_logs/propulsion_dump", exist_ok=True)
    
    logs = []
    # 正常动力包，温度90，压力50
    # TS = 1008 (非异常期)
    pp1 = make_packet(0x1AC5, 5, 101, 1008, make_propulsion_payload(90.5, 50.1))
    logs.append(generate_hex_string(pp1))

    # 异常时间段是 1011 到 1013
    # TS = 1011，温度正常
    pp2 = make_packet(0x1AC5, 5, 102, 1011, make_propulsion_payload(92.0, 51.0))
    logs.append(generate_hex_string(pp2))

    # TS = 1012，温度过载！(超过 90 * 1.5 = 135)
    pp3 = make_packet(0x1AC5, 5, 103, 1012, make_propulsion_payload(145.5, 80.0))
    logs.append(generate_hex_string(pp3))

    # TS = 1013，温度过载！
    pp4 = make_packet(0x1AC5, 5, 104, 1013, make_propulsion_payload(160.2, 85.5))
    logs.append(generate_hex_string(pp4))

    # TS = 1014，恢复正常
    pp5 = make_packet(0x1AC5, 5, 105, 1014, make_propulsion_payload(91.0, 50.5))
    logs.append(generate_hex_string(pp5))

    write_log("downlink_logs/propulsion_dump/propulsion_telemetry.log", logs)

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
