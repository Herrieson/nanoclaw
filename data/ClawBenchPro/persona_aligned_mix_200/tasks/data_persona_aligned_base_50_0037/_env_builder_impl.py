import os
import struct
import random
import math
from datetime import datetime

def build_env():
    os.makedirs("telemetry_dumps", exist_ok=True)
    os.makedirs("recovery", exist_ok=True)
    
    random.seed(86)
    base_ts = 1730000000
    
    with open("telemetry_dumps/downlink_pass_critical.log", "w") as f:
        for i in range(120):
            log_time = datetime.utcfromtimestamp(base_ts + i).isoformat() + "Z"
            prefix = f"[RX {log_time}] RAW_PAYLOAD: "
            
            choice = random.random()
            if choice < 0.65:
                # 包含隐藏在噪声中的有效星象仪数据包
                pre_noise = bytes([random.randint(0, 255) for _ in range(random.randint(2, 18))])
                
                sync = b'\x1a\xcf\xfc\x1d'
                ts_bytes = struct.pack('>I', base_ts + i)
                
                # 生成合法的标准化四元数 (范围在 -1.0 到 1.0 之间)
                u1, u2, u3 = random.random(), random.random(), random.random()
                q1 = math.sqrt(1 - u1) * math.sin(2 * math.pi * u2)
                q2 = math.sqrt(1 - u1) * math.cos(2 * math.pi * u2)
                q3 = math.sqrt(u1) * math.sin(2 * math.pi * u3)
                q4 = math.sqrt(u1) * math.cos(2 * math.pi * u3)
                
                q_bytes = struct.pack('>ffff', q1, q2, q3, q4)
                crc = bytes([random.randint(0, 255), random.randint(0, 255)])
                
                packet = sync + ts_bytes + q_bytes + crc
                post_noise = bytes([random.randint(0, 255) for _ in range(random.randint(2, 18))])
                
                full = pre_noise + packet + post_noise
                hex_str = ' '.join(f'{b:02X}' for b in full)
                f.write(prefix + hex_str + "\n")
                
            elif choice < 0.85:
                # 包含同步字损坏或数据截断的无效包
                pre_noise = bytes([random.randint(0, 255) for _ in range(random.randint(5, 20))])
                # 同步字错了一位或者直接给一堆垃圾数据模拟截断
                bad_sync = b'\x1a\xcf\x00\x1d' 
                garbage_payload = bytes([random.randint(0, 255) for _ in range(22)])
                post_noise = bytes([random.randint(0, 255) for _ in range(random.randint(2, 15))])
                
                full = pre_noise + bad_sync + garbage_payload + post_noise
                f.write(prefix + ' '.join(f'{b:02X}' for b in full) + "\n")
                
            else:
                # 纯信道噪声
                noise = bytes([random.randint(0, 255) for _ in range(random.randint(15, 50))])
                f.write(prefix + ' '.join(f'{b:02X}' for b in noise) + "\n")
                
    # 制造干扰文件，模拟非标准结构的报错堆栈和脏数据
    with open("telemetry_dumps/station_status.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<ground_station id="G-04">\n')
        f.write('  <antenna mode="AUTO_TRACK">WARNING: SIGNAL DEGRADATION</antenna>\n')
        f.write('  <metrics snr="-18.5dB" ber="0.42" pll_lock="FALSE" />\n')
        f.write('  <error_stack>\n')
        f.write('    [1730000005] FATAL: Demodulator sync lost.\n')
        f.write('    [1730000008] WARN: Viterbi decoder correcting massive bit flips.\n')
        f.write('  </error_stack>\n')
        f.write('</ground_station>\n')

if __name__ == "__main__":
    build_env()
