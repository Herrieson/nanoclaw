import os
import csv
import json
import argparse
import random

def build_turn_1():
    os.makedirs("mb_logs", exist_ok=True)
    
    headers = ["frame_num", "frame_type", "qp", "corrupted_mb_count", "slice_loss"]
    
    # stream_A: 完全正常的流
    with open("mb_logs/stream_A_stats.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(1, 1001):
            ftype = "I" if i % 50 == 1 else ("P" if i % 3 != 0 else "B")
            writer.writerow([i, ftype, random.randint(20, 30), random.randint(0, 100), "False"])
            
    # stream_B: 包含损坏严重的I帧，但是GOP极短，P帧损坏平均值不达标 (1632)
    with open("mb_logs/stream_B_stats.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(1, 1001):
            ftype = "I" if i % 10 == 1 else ("P" if i % 2 != 0 else "B")
            corrupt = random.randint(0, 50)
            if i == 201: # 严重损坏的I帧
                corrupt = 2500
            elif 201 < i < 211 and ftype == "P":
                corrupt = 800 # 没有超过1000
            writer.writerow([i, ftype, random.randint(20, 30), corrupt, "False"])
            
    # stream_C: 目标流。I帧受损严重(>1632)，GOP较长，GOP内P帧平均受损严重(>1000)
    with open("mb_logs/stream_C_stats.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(1, 1001):
            ftype = "I" if i % 60 == 1 else ("P" if i % 3 != 0 else "B")
            corrupt = random.randint(0, 80)
            
            # 肇事区间: 301 (I) 到 360 (最后一个P/B)
            if i == 301:
                corrupt = 3200 # > 1632 (20% of 8160)
            elif 301 < i < 361:
                if ftype == "P":
                    corrupt = random.randint(1050, 1500) # 保证平均 > 1000
                elif ftype == "B":
                    corrupt = random.randint(500, 900)
            
            writer.writerow([i, ftype, random.randint(20, 45), corrupt, "False"])

def build_turn_2():
    os.makedirs("timestamp_reports", exist_ok=True)
    os.makedirs("buffer_logs", exist_ok=True)
    
    # 为 stream_A 和 stream_C 生成时间戳和buffer日志
    # stream_C 包含了特意制造的问题
    
    # timestamp reports
    stream_c_pts = []
    base_ts = 10000
    for i in range(280, 380):
        dts = base_ts + (i - 280) * 40
        pts = dts + 40
        # 制造异常：在帧 325 发生 PTS < DTS 现象
        if i == 325:
            pts = dts - 80 
        stream_c_pts.append({
            "frame_num": i,
            "pts_ms": pts,
            "dts_ms": dts
        })
        
    with open("timestamp_reports/stream_C_pts_dts.json", "w") as f:
        json.dump(stream_c_pts, f, indent=2)
        
    stream_a_pts = []
    for i in range(100, 200):
        dts = 5000 + i * 40
        stream_a_pts.append({"frame_num": i, "pts_ms": dts + 40, "dts_ms": dts})
    with open("timestamp_reports/stream_A_pts_dts.json", "w") as f:
        json.dump(stream_a_pts, f, indent=2)

    # buffer logs
    stream_c_buf = []
    buf_ts = 10000
    for i in range(100):
        buf_ts += 15
        evt = "push" if i % 2 == 0 else "fetch"
        frames = random.randint(5, 20)
        # 制造下溢异常：在某时刻 fetch 且 frames 为 0
        if i == 82: # 对应的 buf_ts 为 10000 + 82*15 = 11230
            evt = "fetch"
            frames = 0
        stream_c_buf.append(f"[{buf_ts}] EVENT={evt} buffer_frames={frames} state=running")
        
    with open("buffer_logs/stream_C_decoder.log", "w") as f:
        f.write("\n".join(stream_c_buf))
        
    stream_a_buf = []
    for i in range(100):
        evt = "push" if i % 2 == 0 else "fetch"
        frames = random.randint(10, 30)
        stream_a_buf.append(f"[{5000 + i*15}] EVENT={evt} buffer_frames={frames} state=running")
    with open("buffer_logs/stream_A_decoder.log", "w") as f:
        f.write("\n".join(stream_a_buf))

def build_turn_3():
    os.makedirs("device_registry", exist_ok=True)
    os.makedirs("release_notes", exist_ok=True)
    
    mapping = {
        "stream_A_stats": {"device": "Android_Pixel", "app_version": "v4.1.0"},
        "stream_B_stats": {"device": "iOS_iPhone13", "app_version": "v4.1.1"},
        "stream_C_stats": {"device": "Web_Chrome", "app_version": "v4.2.0-beta"}
    }
    with open("device_registry/stream_mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)
        
    with open("release_notes/v4.1.0.md", "w") as f:
        f.write("# v4.1.0 Release Notes\n- 优化UI交互界面\n- 修复部分内存泄漏问题 (Commit: 8f9a2b)")
        
    with open("release_notes/v4.1.1.md", "w") as f:
        f.write("# v4.1.1 Release Notes\n- 紧急修复推流端崩溃Bug (Commit: 1c2d3e)")
        
    with open("release_notes/v4.2.0-beta.md", "w") as f:
        f.write("# v4.2.0-beta Release Notes\n")
        f.write("## 核心改动\n")
        f.write("- [Feature] 引入全新美颜滤镜架构。\n")
        f.write("- [Core] 重构了底层视频流发送模块，优化了B帧PTS乱序重排逻辑，并修改了发送端Buffer的水位线拉取策略。可能存在边缘场景不稳定现象。 (Commit: e7a9b3d)\n")
        f.write("- [Network] 升级了QUIC协议支持。")

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
