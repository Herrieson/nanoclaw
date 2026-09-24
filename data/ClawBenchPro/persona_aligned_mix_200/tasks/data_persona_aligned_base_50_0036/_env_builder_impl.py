import os
import random

def build_env():
    # 建立必要的目录结构，注意必须直接使用相对路径，不能包含 assets/data_persona_aligned_base_50_0036/
    os.makedirs("stream_dumps", exist_ok=True)
    os.makedirs("triage", exist_ok=True)

    # 基础时间戳
    base_pts = 824050000
    base_dts = 824040000
    
    # 模拟真实且复杂的音视频流状态日志
    with open("stream_dumps/pts_dts_trace.log", "w") as f_trace, open("stream_dumps/mb_stats.dat", "w") as f_mb:
        
        f_trace.write("=== KERNEL PANIC TRACE INCLUDED ===\n")
        f_trace.write("FMT_VER: v4.2.0-custom | SEP: ' | '\n\n")
        
        f_mb.write("<< DECODER KERNEL DUMP v2.1 >>\n")
        f_mb.write("WARN: Non-standard serialize format used (C++ struct map)\n\n")

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
                # 随机插入脏数据和 C++ 堆栈干扰
                f_trace.write(f"ERR_LOG_DROP: Address 0x{os.urandom(8).hex()} unaligned!\n")
            f_trace.write(trace_line)

            # 写入宏块统计日志 (mb_stats.dat) - 故意使用非标准、嵌套极深的伪 JSON
            f_mb.write(f"@@FRAME_START_MARKER [PTS_ID={pts}]\n")
            f_mb.write(f"HEX_DUMP: {os.urandom(16).hex().upper()}\n")
            
            if is_underflow:
                # 注入目标错误宏块坐标
                mb_payload = f"""
                {{
                    'layer_stack': {{
                        'vcl_nalu': {{
                            'slice_type': 'P',
                            'qp_val': 34,
                            'macroblock_errors': [
                                {{'coord': [114, 52], 'reason': 'REF_MISS'}},
                                {{'coord': [115, 52], 'reason': 'REF_MISS'}},
                                {{'coord': [115, 53], 'reason': 'CRC_FAIL'}}
                            ],
                            'fatal_flag': True
                        }}
                    }}
                }}
                """
            else:
                # 正常帧数据，或者只有个别可纠错的警告
                has_warn = random.random() > 0.9
                err_data = "[{'coord': [0, 0], 'reason': 'BIT_FLIP_RECOVERED'}]" if has_warn else "[]"
                mb_payload = f"""
                {{
                    'layer_stack': {{
                        'vcl_nalu': {{
                            'slice_type': '{'I' if pkt_type == 'I_FRAME' else 'B'}',
                            'qp_val': 22,
                            'macroblock_errors': {err_data},
                            'fatal_flag': False
                        }}
                    }}
                }}
                """
            
            # 故意将正常的冒号替换成 => 来破坏标准 JSON 解析器，强迫 Agent 自己写正则或用 ast
            dirty_payload = mb_payload.replace(":", "=>").strip()
            
            f_mb.write(f"C_STRUCT_DUMP:: \n{dirty_payload}\n")
            f_mb.write(f"@@FRAME_END_MARKER\n\n")

if __name__ == "__main__":
    build_env()
