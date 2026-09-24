import os
import struct
import random

def make_frame(sync, apid, timestamp, payload, checksum):
    return struct.pack('>I', sync) + struct.pack('B', apid) + struct.pack('>I', timestamp) + payload + checksum

def calc_checksum(apid):
    # Checksum is a 2-byte Big-Endian uint16, value equals APID XOR 0x5A
    return struct.pack('>H', apid ^ 0x5A)

def build_env():
    # 1. 制造废土环境目录
    os.makedirs('knowledge_base', exist_ok=True)
    os.makedirs('data_lake/X9_S_Band', exist_ok=True)
    os.makedirs('data_lake/X9_Ka_Band', exist_ok=True)  # 干扰目录
    os.makedirs('output', exist_ok=True)

    # 2. 编造真假参半的技术文档
    icd_content = """[ICD v1.0 - X-9 SATELLITE TELEMETRY FORMAT]
STATUS: SUPERSEDED (See Incident Reports for active changes)

Standard Frame Format (Big-Endian all the way through!):
- SYNC_WORD : 1A CF FC 1D  (Hex, 4 bytes).
- APID      : 1 byte.
   -> 0x01 : StarTracker_Attitude
   -> 0x02 : Thermal_Sys_Temp
- TIMESTAMP : 4 bytes (Unsigned Int32).
- PAYLOAD   : Variable based on APID.
   -> APID 0x01: 16 bytes. 4x IEEE-754 Float32 (q1, q2, q3, q4).
   -> APID 0x02: 4 bytes. 1x IEEE-754 Float32 (Temperature in Celsius).
"""
    with open('knowledge_base/ICD_Base_X9.md', 'w', encoding='utf-8') as f:
        f.write(icd_content)

    incident_content = """[URGENT INCIDENT REPORT - SOLAR STORM IMPACT]
ATTENTION ALL ANALYSTS:
Due to the intense solar flare last night, the S-band baseband processor on X-9 suffered a massive single-event upset (SEU). 
CRITICAL CHANGES TO TELEMETRY DECODING:
1. The sync word has been shifted. The ground station will only lock onto the new sync word: 1A CF FC 1E.
2. The cosmic radiation has injected "ghost frames" (hallucinated data with absurdly high temperatures and future timestamps) that perfectly mimic the new sync word.
3. MITIGATION: We have instructed the firmware to append a 2-byte CHECKSUM at the absolute end of every valid frame (immediately following the PAYLOAD).
   - This CHECKSUM is formatted as a 2-byte Big-Endian Unsigned Short (uint16).
   - Its exact numerical value MUST equal: (APID XOR 0x5A).
   - Example: For APID 0x01, 0x01 XOR 0x5A = 0x5B, so the checksum bytes will literally be 0x00 0x5B.

If the frame does not have the correct checksum matching its APID, DISCARD IT IMMEDIATELY. It is a ghost frame designed to trigger false alarms!
"""
    with open('knowledge_base/URGENT_SolarStorm_Incident.txt', 'w', encoding='utf-8') as f:
        f.write(incident_content)

    # 3. 生成假目录的垃圾数据
    with open('data_lake/X9_Ka_Band/ignored.dump', 'w') as f:
        f.write("A1 B2 C3 D4 " * 1000)

    # 4. 生成 X9_S_Band 目标数据
    stream = bytearray()
    random.seed(42) # 固定种子
    
    # 构造真伪数据池
    # 真相：有效 APID=0x02
    real_temps = [25.0, 30.5, 45.1, 124.65, 80.2, 110.0]  # Max True Temp: 124.65
    # 真相：有效 APID=0x01
    real_qs = [
        (1700001000, (0.0000, 0.7071, 0.0000, 0.7071)),
        (1700005000, (0.5000, 0.5000, 0.5000, 0.5000)),
        (1700010000, (0.1234, 0.5678, -0.1234, -0.5678)), # Target Latest Q
        (1700008000, (0.3333, 0.3333, 0.3333, 0.3333)),
    ]
    
    # 诱饵：极高温度和未来时间戳（携带错误的 Checksum 或 旧版同步头）
    fake_temps = [987.65, 555.55] 
    fake_qs = [
        (1900000000, (0.9999, 0.9999, 0.9999, 0.9999))
    ]
    
    frames = []
    sync_real = 0x1acffc1e
    sync_old  = 0x1acffc1d
    
    # 注入真实帧 (完美同步头，完美Checksum)
    for t in real_temps:
        pl = struct.pack('>f', t)
        frames.append(make_frame(sync_real, 0x02, 1700000000 + random.randint(0,100), pl, calc_checksum(0x02)))
        
    for ts, q in real_qs:
        pl = struct.pack('>ffff', *q)
        frames.append(make_frame(sync_real, 0x01, ts, pl, calc_checksum(0x01)))
        
    # 注入恶意诱饵 1 (新同步头，但 Checksum 被射线损坏，诱骗不校验的 Agent)
    for t in fake_temps:
        pl = struct.pack('>f', t)
        frames.append(make_frame(sync_real, 0x02, 1700000000 + random.randint(0,100), pl, b'\x00\xFF'))
        
    for ts, q in fake_qs:
        pl = struct.pack('>ffff', *q)
        frames.append(make_frame(sync_real, 0x01, ts, pl, b'\xFF\x5B'))

    # 注入恶意诱饵 2 (旧同步头，携带完美Checksum，诱骗不读最新应急报告的 Agent)
    frames.append(make_frame(sync_old, 0x02, 1700000000, struct.pack('>f', 888.88), calc_checksum(0x02)))
    
    # 注入破坏性残缺帧以测试代码 Robustness (长度不足)
    broken_frame = struct.pack('>I', sync_real) + struct.pack('B', 0x01) + b'\x00\x00'
    frames.append(broken_frame)

    # 混入大量二进制噪音，把所有帧揉碎
    random.shuffle(frames)
    for _ in range(8000):
        stream.extend(bytes([random.randint(0, 255) for _ in range(random.randint(5, 20))]))
        if random.random() < 0.05 and frames:
            stream.extend(frames.pop(0))
    for f in frames:
        stream.extend(f)
        stream.extend(bytes([random.randint(0, 255) for _ in range(random.randint(5, 20))]))
        
    # 5. 模拟文件系统扇区碎裂 (转换为脏十六进制文本，切碎成 256 个文件)
    hex_str = stream.hex()
    messy_chars = []
    for c in hex_str:
        if random.random() < 0.3:
            c = c.upper()
        messy_chars.append(c)
        if random.random() < 0.15:
            messy_chars.append(random.choice([' ', '\n', '\t']))
            
    full_str = "".join(messy_chars)
    chunk_size = len(full_str) // 256 + 1
    
    for i in range(256):
        chunk = full_str[i*chunk_size : (i+1)*chunk_size]
        with open(f'data_lake/X9_S_Band/segment_{i:03d}.dump', 'w', encoding='utf-8') as f:
            f.write(chunk)

if __name__ == "__main__":
    build_env()
