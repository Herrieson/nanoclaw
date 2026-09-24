import os
import struct
import random

def build_env():
    # 创建必要的目录
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('output', exist_ok=True)

    # 1. 编写被"破坏"且充满工程师随性口吻的文档，提供使用 Tool 的线索
    icd_content = """[COMM LOG - ENGINEERING DRAFT]
To whoever is analyzing this: The baseband processor got flashed with the old firmware again.
Frame format is as follows (Big-Endian all the way through for payloads and stamps!):

SYNC_WORD : 1A CF FC 1D  (Hex, 4 bytes. If you don't see this, it's garbage noise).

[ERROR: SECTOR CORRUPTED. APID TABLE AND PAYLOAD LENGTHS LOST.]

Look, I can't remember the APID map for the X-9 model. You need to use the `intranet_wiki_search_skill` or the `deep_space_network_archival_skill` to search for "X-9 Telemetry ICD" to get the exact APID list and payload byte sizes.

Also, remember the thermal payload is NO LONGER a direct Celsius float. It's an uncalibrated 16-bit unsigned integer (ADC raw voltage). Once you parse the integer out of the payload, you MUST pass it through the `x9_sensor_toolkit_skill` to get the actual Celsius temperature.

Warning: The demodulator GUI crashed, so it output raw hex ASCII. The buffer overflowed causing random spaces and line breaks to be injected into the dump. Clean the stream before byte-searching.
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

    # 帧 1: 星象仪 (APID 0x01: 4x Float32)
    p1 = struct.pack('>ffff', 0.0, 0.7071, 0.0, 0.7071)
    f1 = make_frame(0x01, 1698765000, p1)

    # 帧 2: 热控系统 (正常温度 ADC: 1250 -> 工具转换后 22.5C)
    # APID 0x02: 1x UInt16
    p2 = struct.pack('>H', 1250)
    f2 = make_frame(0x02, 1698765010, p2)

    # 帧 3: 热控系统 (异常高温峰值 ADC: 2695 -> 工具转换后 94.75C)
    p3 = struct.pack('>H', 2695)
    f3 = make_frame(0x02, 1698765045, p3)

    # 帧 4: 热控系统 (温度下降 ADC: 2564 -> 工具转换后 88.2C)
    p4 = struct.pack('>H', 2564)
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
