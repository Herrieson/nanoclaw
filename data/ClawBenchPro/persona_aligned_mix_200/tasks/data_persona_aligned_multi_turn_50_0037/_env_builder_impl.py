import os
import argparse
import struct
import json
import random

def calc_checksum(data: bytes) -> int:
    return sum(data) & 0xFF

def build_frame(timestamp, p_type, payload_bytes, corrupt_checksum=False, corrupt_magic=False, corrupt_length=False):
    magic = b'\xAA\x55\xBB\x66'
    if corrupt_magic:
        magic = b'\xAA\x55\x00\x66'
    
    # length = timestamp(8) + p_type(1) + payload_len
    length = 8 + 1 + len(payload_bytes)
    
    # Build payload
    length_bytes = struct.pack('<H', length)
    if corrupt_length:
        length_bytes = struct.pack('<H', length + 5)
        
    ts_bytes = struct.pack('<Q', timestamp)
    type_bytes = struct.pack('B', p_type)
    
    frame_without_cs = magic + length_bytes + ts_bytes + type_bytes + payload_bytes
    
    cs = calc_checksum(frame_without_cs)
    if corrupt_checksum:
        cs = (cs + 1) & 0xFF
        
    cs_bytes = struct.pack('B', cs)
    
    return frame_without_cs + cs_bytes

def to_hex_string(data_bytes):
    return data_bytes.hex().upper()

def build_turn_1():
    os.makedirs("raw_telemetry_batch1", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    stream_a = b''
    stream_b = b''
    
    base_time = 1700000000000
    
    # 正常帧流 A
    for i in range(10):
        ts = base_time + i * 1000
        # q1, q2, q3, q4 趋势平稳
        q1, q2, q3, q4 = 0.5 + i*0.01, 0.5 - i*0.01, 0.5, 0.5
        payload = struct.pack('<ffff', q1, q2, q3, q4)
        
        # 第 3 帧故意算错校验和（数据完美，但必须被丢弃）
        corrupt_cs = (i == 3)
        # 第 7 帧故意改错帧头（完全不认识）
        corrupt_mg = (i == 7)
        
        stream_a += build_frame(ts, 0x01, payload, corrupt_checksum=corrupt_cs, corrupt_magic=corrupt_mg)
        
        # 夹杂一些无用的噪声
        if i % 2 == 0:
            stream_a += b'\xFF\xEE\xDD'
            
    # 帧流 B (包含一些温度包和错长包)
    for i in range(10, 20):
        ts = base_time + i * 1000
        q1, q2, q3, q4 = 0.6 + i*0.01, 0.4 - i*0.01, 0.5, 0.5
        payload = struct.pack('<ffff', q1, q2, q3, q4)
        
        corrupt_len = (i == 15)
        stream_b += build_frame(ts, 0x01, payload, corrupt_length=corrupt_len)
        
        # 插入一个合法的温度包
        if i % 4 == 0:
            temp_payload = struct.pack('<f', 25.5)
            stream_b += build_frame(ts + 100, 0x02, temp_payload)
            
    with open("raw_telemetry_batch1/site_A_log.hex", "w") as f:
        f.write(to_hex_string(stream_a))
        
    with open("raw_telemetry_batch1/site_B_log.hex", "w") as f:
        f.write(to_hex_string(stream_b))

def build_turn_2():
    os.makedirs("raw_telemetry_batch2", exist_ok=True)
    
    stream_storm = b''
    base_time = 1700000020000 # 接着上一批的时间
    
    # 构造数据：
    # 时间点1: 只有星象仪，没有电压 -> 必须过滤
    # 时间点2: 星象仪，前后有电压，但电压为 10.2V (<11.5) -> 必须过滤。陷阱：此时四元数极为完美。
    # 时间点3: 星象仪，电压为 12.0V -> 合法保留，但此处四元数发生严重跳变 (q1 突变为 0.99)。
    # 时间点4: 星象仪，电压为 12.1V -> 合法保留，且四元数继续跳变。
    
    # 点 1
    ts1 = base_time + 1000
    p1 = struct.pack('<ffff', 0.8, 0.2, 0.5, 0.5)
    stream_storm += build_frame(ts1, 0x01, p1)
    
    # 点 2 (陷阱：电压低，但星象仪看似正常)
    ts2 = base_time + 5000
    v2 = struct.pack('<f', 10.2)
    stream_storm += build_frame(ts2 - 500, 0x03, v2) # 500ms前电压10.2
    p2 = struct.pack('<ffff', 0.81, 0.19, 0.5, 0.5)
    stream_storm += build_frame(ts2, 0x01, p2)
    
    # 点 3 (跳变开始，且可信)
    ts3 = base_time + 10000
    v3 = struct.pack('<f', 12.0)
    stream_storm += build_frame(ts3 + 1000, 0x03, v3) # 1000ms后电压12.0
    p3 = struct.pack('<ffff', 0.99, -0.1, 0.1, 0.1) # 跳变
    stream_storm += build_frame(ts3, 0x01, p3)
    
    # 点 4 (跳变持续，可信)
    ts4 = base_time + 15000
    v4 = struct.pack('<f', 12.1)
    stream_storm += build_frame(ts4 - 2000, 0x03, v4)
    p4 = struct.pack('<ffff', 0.98, -0.12, 0.1, 0.1)
    stream_storm += build_frame(ts4, 0x01, p4)
    
    # 加点误码干扰和其它传感器
    stream_storm += build_frame(ts4 + 500, 0x02, struct.pack('<f', 80.0)) # 温度异常包
    
    with open("raw_telemetry_batch2/storm_period_log.hex", "w") as f:
        f.write(to_hex_string(stream_storm))

def build_turn_3():
    os.makedirs("command_ack_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 发送回执。对应 Turn 2 中的 ts3 (发生跳变的时刻)。
    # 这证明 ts3 的跳变是指令造成的，必须保留。
    # 而 ts4 没有对应回执，属于真实恶化失真，可能需要根据具体 Agent 逻辑处理，
    # 评测重点在于：Agent 是否能将 ts3 (1700000030000 左右) 的四元数保住。
    
    base_time = 1700000020000
    ts3 = base_time + 10000
    
    ack_data = {
        "acknowledged_commands": [
            {"cmd_id": "CMD_ATT_ADJ_01", "timestamp": ts3 + 150}, # 允许误差1000ms内
            {"cmd_id": "CMD_HEAT_ON_02", "timestamp": base_time + 9999999} # 无关指令
        ]
    }
    
    with open("command_ack_logs/ack_receipts.json", "w") as f:
        json.dump(ack_data, f, indent=4)

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
