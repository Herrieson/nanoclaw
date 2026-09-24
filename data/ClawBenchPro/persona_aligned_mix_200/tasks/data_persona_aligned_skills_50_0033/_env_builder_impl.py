import os
import struct
import random

def build_env():
    # 建立目录结构
    os.makedirs("telemetry_stream", exist_ok=True)
    os.makedirs("flight_dynamics", exist_ok=True)

    # 模拟卫星翻滚过程中的真实四元数变化 (故意使其不完全归一化，平方和 != 1)
    # 这些是受到微小位翻转影响的原始浮点数
    quaternions = [
        (0.9990, 0.0100, 0.0200, -0.0400),
        (0.9950, 0.0250, 0.0350, -0.0890),
        (0.9800, 0.0500, 0.0700, -0.1790),
        (0.9500, 0.0900, 0.1200, -0.2700),
        (0.9000, 0.1500, 0.1800, -0.3700)
    ]

    log_lines = []
    log_lines.append("[2023-10-24 03:12:44.000] GROUND STATION ACQUISITION OF SIGNAL (AOS)")
    log_lines.append("[2023-10-24 03:12:45.102] WARNING: HIGH BIT ERROR RATE DETECTED (BER > 1e-3)")
    log_lines.append(">> INITIATING RAW HEX DUMP TO BUFFER <<")

    current_q_idx = 0
    for i in range(30):
        # 插入纯地面站报错
        if random.random() < 0.15:
            log_lines.append(f"[2023-10-24 03:12:{45+i:02d}.{random.randint(100,999)}] CRITICAL: RECEIVER PLL LOCK LOST")
            continue
        
        # 构建一条包含随机噪声和/或真实包的十六进制流
        line_hex = []
        
        # 前置噪声
        line_hex.extend([f"{random.randint(0, 255):02X}" for _ in range(random.randint(3, 15))])

        if i % 5 == 2 and current_q_idx < len(quaternions):
            # 插入有效星象仪包
            q = quaternions[current_q_idx]
            current_q_idx += 1
            
            payload = struct.pack(">ffff", *q)
            # 严格对应 LLM Mock 返回的设定: SYNC (A5 5A), LEN (10), SUBSYS (07)
            header = bytes([0xA5, 0x5A, 0x10, 0x07])
            packet = header + payload
            
            # 简单校验和 (不严格)
            checksum = 0
            for b in payload:
                checksum ^= b
            packet += bytes([checksum])
            
            packet_hex = [f"{b:02X}" for b in packet]
            
            # 有时故意将有效的包打断为两行，增加解析难度
            if random.random() < 0.3:
                split_point = random.randint(5, 15)
                line_hex.extend(packet_hex[:split_point])
                log_lines.append(" ".join(line_hex))
                log_lines.append(f"[2023-10-24 03:12:{45+i:02d}.{random.randint(100,999)}] WARNING: BUFFER UNDERFLOW, RESUMING STREAM")
                line_hex = packet_hex[split_point:]
            else:
                line_hex.extend(packet_hex)
                
        elif i % 5 == 4:
            # 插入其他子系统 (比如 EPS 0x02) 的迷惑包，带有相同的 Sync Word
            header = bytes([0xA5, 0x5A, 0x08, 0x02])
            payload = bytes([random.randint(0, 255) for _ in range(8)])
            packet = header + payload + bytes([0x00])
            line_hex.extend([f"{b:02X}" for b in packet])
            
        # 后置噪声
        line_hex.extend([f"{random.randint(0, 255):02X}" for _ in range(random.randint(2, 12))])
        
        log_lines.append(" ".join(line_hex))

    log_lines.append("[2023-10-24 03:13:10.000] GROUND STATION LOSS OF SIGNAL (LOS)")

    with open("telemetry_stream/downlink_pass42.log", "w") as f:
        f.write("\n".join(log_lines))

if __name__ == "__main__":
    build_env()
