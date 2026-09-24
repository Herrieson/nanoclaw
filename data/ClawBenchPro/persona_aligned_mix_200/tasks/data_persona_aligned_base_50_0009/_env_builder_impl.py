import os
import struct
import random

def build_env():
    # 创建必要的目录
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('output', exist_ok=True)

    # 1. 编写充满工程师随性口吻的非标准文档
    icd_content = """[COMM LOG - ENGINEERING DRAFT]
To whoever is analyzing this: The baseband processor got flashed with the old firmware again.
Frame format is as follows (Big-Endian all the way through for payloads and stamps!):

SYNC_WORD : 1A CF FC 1D  (Hex, 4 bytes. If you don't see this, it's garbage noise).
APID : 1 byte immediately following sync word.
   -> 0x01 : StarTracker_Attitude
   -> 0x02 : Thermal_Sys_Temp
TIMESTAMP : 4 bytes (Unsigned Int32. The ground station clocks are synced to this).
PAYLOAD : Length varies by APID.
   - If APID 01: 16 bytes total. 4x IEEE-754 Float32. Represents q1, q2, q3, q4.
   - If APID 02: 4 bytes total. 1x IEEE-754 Float32. Represents temperature in Celsius.

Warning: The demodulator GUI crashed, so it output raw hex ASCII. The buffer overflowed causing random spaces and line breaks to be injected into the dump. You'll have to clean the stream before byte-searching.
"""
    with open('docs/ICD_notes.txt', 'w', encoding='utf-8') as f:
        f.write(icd_content)

    # 2. 构造模拟的二进制遥测数据
    def make_frame(apid, timestamp, payload_bytes):
        frame = b'\x1a\xcf\xfc\x1d'
        frame += struct.pack('B', apid)
        frame += struct.pack('>I', timestamp)
        frame += payload_bytes
        return frame

    # 帧 1: 星象仪 (旧数据)
    p1 = struct.pack('>ffff', 0.0, 0.7071, 0.0, 0.7071)
    f1 = make_frame(0x01, 1698765000, p1)

    # 帧 2: 热控系统 (正常温度)
    p2 = struct.pack('>f', 22.5)
    f2 = make_frame(0x02, 1698765010, p2)

    # 帧 3: 热控系统 (异常高温峰值!)
    p3 = struct.pack('>f', 94.75)
    f3 = make_frame(0x02, 1698765045, p3)

    # 帧 4: 热控系统 (温度下降)
    p4 = struct.pack('>f', 88.2)
    f4 = make_frame(0x02, 1698765050, p4)

    # 帧 5: 星象仪 (最新数据!)
    p5 = struct.pack('>ffff', 0.4999, 0.5001, -0.4999, -0.5001)
    f5 = make_frame(0x01, 1698765080, p5)

    # 组合成数据流，注入大量随机噪点和误码
    random.seed(42) # 固定种子确保沙盒可复现
    stream = bytearray()
    stream.extend(bytes([random.randint(0, 255) for _ in range(150)]))
    stream.extend(f1)
    stream.extend(bytes([random.randint(0, 255) for _ in range(78)]))
    stream.extend(f2)
    stream.extend(bytes([random.randint(0, 255) for _ in range(233)]))
    stream.extend(f3)
    stream.extend(bytes([random.randint(0, 255) for _ in range(45)]))
    
    # 注入一个被破坏的帧头以测试鲁棒性
    stream.extend(b'\x1a\xcf\xfc\x1c' + struct.pack('B', 0x01) + struct.pack('>I', 1698765090) + p1)
    
    stream.extend(bytes([random.randint(0, 255) for _ in range(102)]))
    stream.extend(f4)
    stream.extend(bytes([random.randint(0, 255) for _ in range(88)]))
    stream.extend(f5)
    stream.extend(bytes([random.randint(0, 255) for _ in range(320)]))

    # 转换为极其凌乱的十六进制文本格式
    hex_str = stream.hex()
    messy_dump = []
    for i in range(len(hex_str)):
        messy_dump.append(hex_str[i])
        # 随机注入干扰字符（空格、换行、大写字母混用）
        if random.random() < 0.15:
            messy_dump.append(" ")
        if random.random() < 0.05:
            messy_dump.append("\n")
            
    final_dump_str = "".join(messy_dump)
    # 随机大写化部分字符
    final_dump_str = "".join([c.upper() if random.random() < 0.3 else c for c in final_dump_str])

    with open('raw_data/downlink_stream.dump', 'w', encoding='utf-8') as f:
        f.write(final_dump_str)

if __name__ == "__main__":
    build_env()
