import os
import random
import json

def build_env():
    # 建立必要的目录结构，使用相对路径
    os.makedirs("stream_dumps", exist_ok=True)
    os.makedirs("triage", exist_ok=True)
    os.makedirs(".mock_backend", exist_ok=True)  # 用于存放 API 背后真实数据的隐藏目录

    # 基础时间戳
    base_pts = 824050000
    base_dts = 824040000
    
    db_data = {}
    
    # 模拟真实且复杂的音视频流状态日志
    with open("stream_dumps/pts_dts_trace.log", "w") as f_trace:
        f_trace.write("=== KERNEL PANIC TRACE INCLUDED ===\n")
        f_trace.write("FMT_VER: v4.2.0-custom | SEP: ' | '\n\n")
        
        # 生成 300 帧的数据
        for i in range(300):
            pts = base_pts + i * 3600
            dts = base_dts + i * 3600
            
            # 正常情况下缓冲区水位在 1M - 8M 之间波动
            buf_lvl = random.randint(1024000, 8388608)
            
            # 在第 173 帧注入 Buffer Underflow 异常
            is_underflow = False
            if i == 173:
                buf_lvl = -40960  # 致命下溢
                is_underflow = True
            
            # 添加一些噪声包 (如 B 帧 / P 帧的抖动)
            pkt_type = random.choice(["I_FRAME", "P_FRAME", "B_FRAME", "AUDIO_AAC"])
            hex_offset = os.urandom(4).hex().upper()
            
            # 写入时间戳追踪日志（非标准格式）
            trace_line = f"[{i:05d}] <PKT:{pkt_type}> | PTS: {pts} | DTS: {dts} | OFFSET: 0x{hex_offset} | BUF_LVL: {buf_lvl} bytes | FLAGS: 0x00\n"
            if i % 15 == 0 and not is_underflow:
                f_trace.write(f"ERR_LOG_DROP: Address 0x{os.urandom(8).hex()} unaligned!\n")
            f_trace.write(trace_line)

            # 将宏块数据写入隐藏的 Mock DB 而不是明文文件
            if is_underflow:
                db_data[str(pts)] = {
                    "slice_type": "P",
                    "fatal_flag": True,
                    "macroblock_errors": [
                        {"coord": [114, 52], "reason": "REF_MISS"},
                        {"coord": [115, 52], "reason": "REF_MISS"},
                        {"coord": [115, 53], "reason": "CRC_FAIL"}
                    ]
                }
            else:
                has_warn = random.random() > 0.95
                if has_warn:
                    db_data[str(pts)] = {
                        "slice_type": "I" if pkt_type == "I_FRAME" else "B",
                        "fatal_flag": False,
                        "macroblock_errors": [{"coord": [0, 0], "reason": "BIT_FLIP_RECOVERED"}]
                    }

    # 生成一个无法直接读取的假二进制核心 Dump 文件
    with open("stream_dumps/video_stream_dump.bin", "wb") as f_bin:
        # 写入 512KB 的随机二进制垃圾数据
        f_bin.write(os.urandom(1024 * 512))
        
    # 保存后台 Mock 数据库，供 StreamVision API Skill 读取
    with open(".mock_backend/stream_vision_db.json", "w") as f_db:
        json.dump(db_data, f_db)

if __name__ == "__main__":
    build_env()
