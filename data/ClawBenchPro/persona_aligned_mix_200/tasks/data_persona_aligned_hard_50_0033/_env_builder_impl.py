import os
import struct
import random
import json
import math

def build_env():
    # 建立废土目录结构
    os.makedirs("telemetry_stream/raw_buffers", exist_ok=True)
    os.makedirs("flight_dynamics", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("communications/emails", exist_ok=True)

    # 1. 误导性的基础 ICD 文档 (旧版本)
    icd_content = """NOVA-7 SATELLITE ICD v1.0
STATUS: DEPRECATED (Refer to recent update memos if applicable)

--- FRAME STRUCTURE ---
[SYNC_WORD] [PAYLOAD_LEN] [SUBSYS_ID] [PAYLOAD] [CHECKSUM]
1. SYNC_WORD: 0xA5 0x5A
2. PAYLOAD_LEN: 1 Byte.
3. SUBSYS_ID: 1 Byte. 
   - 0x02: EPS (Power)
   - 0x07: STR (Star Tracker Attitude Data)  << DEFAULT
   - 0x09: COMM (Communications)
4. PAYLOAD: Variable
5. CHECKSUM: 1 Byte XOR

--- STAR TRACKER (0x07) ---
Len: 0x10. Format: Four IEEE 754 float32 in Big-Endian.
Order: q_w, q_x, q_y, q_z
"""
    with open("docs/base_icd_v1.0.txt", "w") as f:
        f.write(icd_content)

    # 2. 隐藏在邮件里的真理 (线索)
    email_content = """From: jim.halpert@nova.sys
To: cdh_team@nova.sys
Subject: RE: URGENT: I2C Bus collision on Star Tracker
Date: 2023-10-18

Guys, the hotfix is deployed. We had to move the Star Tracker off the primary I2C bus because EPS was drowning it out. 

CRITICAL CHANGES IN FW v1.4.2:
1. The Subsystem ID for Star Tracker is now shifted to 0x1E (was 0x07).
2. We had to use the new coprocessor for the math, and unfortunately, it's Little-Endian. So the 4 floats for the quaternions are now packed in Little-Endian instead of Big-Endian. 
Make sure you update the parsers on the ground station! I don't have time to update the ICD doc right now.

Cheers,
Jim
"""
    with open("communications/emails/fw_update_notice_HOTFIX.eml", "w") as f:
        f.write(email_content)
        
    # 加入几个干扰邮件
    with open("communications/emails/lunch_break.eml", "w") as f:
        f.write("Anyone down for tacos? The cafeteria is serving them today.")

    # 3. 构造庞大的连续字节流环境 (100 KB)
    TOTAL_BYTES = 100000
    stream_buffer = bytearray(os.urandom(TOTAL_BYTES)) # 随机噪音底色

    # 真实数据轨迹生成 (30个平滑旋转的四元数)
    true_quaternions = []
    for i in range(30):
        t = i * 0.1
        w = math.cos(t)
        x = math.sin(t) * 0.5
        y = math.sin(t) * 0.5
        z = math.sin(t) * 0.707
        norm = math.sqrt(w*w + x*x + y*y + z*z)
        true_quaternions.append((w/norm, x/norm, y/norm, z/norm))

    # 伪造假包 (误导那些直接用 0x07 和 Big Endian 的 Agent)
    fake_positions = random.sample(range(0, TOTAL_BYTES - 30), 80)
    for pos in fake_positions:
        header = bytes([0xA5, 0x5A, 0x10, 0x07])
        # 故意给一些奇怪的值，或者全零
        payload = struct.pack(">ffff", 0.0, 0.0, 0.0, 0.0) 
        chk = 0
        for b in payload: chk ^= b
        packet = header + payload + bytes([chk])
        for i, b in enumerate(packet):
            stream_buffer[pos + i] = b

    # 植入真包 (0x1E, Little Endian)
    # 确保位置不和假包重叠
    valid_positions = []
    while len(valid_positions) < len(true_quaternions):
        p = random.randint(0, TOTAL_BYTES - 30)
        overlap = False
        for fp in fake_positions:
            if abs(p - fp) < 30: overlap = True
        for vp in valid_positions:
            if abs(p - vp) < 30: overlap = True
        if not overlap:
            valid_positions.append(p)
            
    valid_positions.sort() # 按顺序排列，符合时间序列
    
    for idx, pos in enumerate(valid_positions):
        header = bytes([0xA5, 0x5A, 0x10, 0x1E])
        payload = struct.pack("<ffff", *true_quaternions[idx])
        chk = 0
        for b in payload: chk ^= b
        packet = header + payload + bytes([chk])
        for i, b in enumerate(packet):
            stream_buffer[pos + i] = b

    # 转为大写十六进制字符串
    hex_string = stream_buffer.hex().upper()

    # 插入乱码和错误日志文本 (打断 HEX 的连续性，增加提取难度)
    mixed_content = []
    cursor = 0
    while cursor < len(hex_string):
        # 随机截取一段 HEX
        chunk_len = random.randint(10, 150)
        mixed_content.append(hex_string[cursor : cursor + chunk_len])
        cursor += chunk_len
        
        # 随机插入系统崩溃文本
        if random.random() < 0.1:
            errors = [
                "\n[FATAL] KERNEL PANIC: VFS SYNC FAILED\n",
                "\n[WARN] WATCHDOG TIMEOUT ON BUS 2\n",
                "\n<<< BUFFER UNDERFLOW >>>\n",
                "\n[SYS] IO BLOCK READ TIMEOUT: SECTOR CORRUPTED\n",
                "\n"
            ]
            mixed_content.append(random.choice(errors))

    full_text = "".join(mixed_content)

    # 将这个巨大的字符串切分成几百个小文件，散落分布
    # 注意：帧可能正好在文件边界处被切断！
    FILE_COUNT = 200
    chars_per_file = len(full_text) // FILE_COUNT
    
    for i in range(FILE_COUNT):
        start = i * chars_per_file
        # 最后一个文件收尾
        end = (i + 1) * chars_per_file if i < FILE_COUNT - 1 else len(full_text)
        
        file_name = f"telemetry_stream/raw_buffers/frag_{i:03d}.log"
        with open(file_name, "w") as f:
            f.write(full_text[start:end])

if __name__ == "__main__":
    build_env()
