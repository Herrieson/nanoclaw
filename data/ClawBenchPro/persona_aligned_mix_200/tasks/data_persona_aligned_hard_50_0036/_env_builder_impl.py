import os
import json
import random

def build_env():
    # 建立目录结构，严格使用相对路径
    os.makedirs("edge_dumps/configs", exist_ok=True)
    os.makedirs("edge_dumps/traces", exist_ok=True)
    os.makedirs("edge_dumps/mb_stats", exist_ok=True)
    os.makedirs("triage", exist_ok=True)

    target_channel = "S10_Finals_Main"
    target_stream = "ST_8X2A"
    target_pts = 824888000
    target_coords = [[114, 52], [115, 52], [115, 53]]

    # 1. 制造 Configs 碎片（路由注册表）
    # 共计 20 个文件，10000 个频道，只隐藏 1 个目标流 ID
    channel_id_counter = 1000
    for i in range(20):
        config_data = {}
        for j in range(500):
            if i == 13 and j == 250:
                config_data[target_channel] = {"stream_id": target_stream, "priority": "high"}
            else:
                fake_channel = f"Channel_Auto_{channel_id_counter}"
                fake_stream = f"ST_{os.urandom(2).hex().upper()}"
                config_data[fake_channel] = {"stream_id": fake_stream, "priority": random.choice(["low", "mid", "high"])}
                channel_id_counter += 1
        
        with open(f"edge_dumps/configs/route_{i:02d}.json", "w") as f:
            json.dump({"registry_version": "v3.1", "routes": config_data}, f, indent=2)

    # 2. 制造 Traces 和 MB Stats（大规模噪音与干扰）
    streams = [target_stream] + [f"ST_{os.urandom(2).hex().upper()}" for _ in range(99)]
    pts_counter = 100000000
    
    # 50 个 Trace 文件和 MB Stats 文件，共计 50000 帧数据
    for i in range(50):
        with open(f"edge_dumps/traces/trace_{i:02d}.log", "w") as ft, \
             open(f"edge_dumps/mb_stats/mb_dump_{i:02d}.dat", "w") as fm:
            
            ft.write(f"=== TRACE CHUNK {i} ===\n")
            fm.write(f"<< MB STATS CHUNK {i} >>\n")

            for j in range(1000):
                is_target = (i == 37 and j == 412)
                
                if is_target:
                    strm = target_stream
                    pts = target_pts
                    buf_lvl = -4096
                else:
                    strm = random.choice(streams)
                    pts = pts_counter
                    # 噪音注入：其他流也会发生下溢（负数），诱导使用暴力 grep 的 Agent 踩坑
                    if strm != target_stream and random.random() < 0.05:
                        buf_lvl = random.randint(-5000, -1)
                    else:
                        buf_lvl = random.randint(1024, 8388608)
                
                pts_counter += random.randint(1000, 5000)
                pkt_type = random.choice(["I_FRAME", "P_FRAME", "B_FRAME"])

                # Trace logs (多行结构，阻断简单的单行正则匹配)
                ft.write("--FRAME--\n")
                ft.write(f"STRM: {strm}\n")
                ft.write(f"PKT: {pkt_type}\n")
                ft.write(f"PTS: {pts}\n")
                ft.write(f"BUF_LVL: {buf_lvl}\n")
                ft.write("---------\n")

                # MB Stats (非标准 C++ 结构体字符串)
                fm.write(f"@@FRAME_START_MARKER [PTS_ID={pts}]\n")
                fm.write(f"HEX_DUMP: {os.urandom(8).hex().upper()}\n")
                
                if is_target:
                    err_data = f"""[
                        {{'coord'=> [{target_coords[0][0]}, {target_coords[0][1]}], 'reason'=> 'REF_MISS'}},
                        {{'coord'=> [{target_coords[1][0]}, {target_coords[1][1]}], 'reason'=> 'REF_MISS'}},
                        {{'coord'=> [{target_coords[2][0]}, {target_coords[2][1]}], 'reason'=> 'CRC_FAIL'}}
                    ]"""
                else:
                    # 噪音注入：即使是正常的帧，也可能包含假的报错坐标
                    has_err = random.random() < 0.1
                    if has_err:
                        err_data = f"[{{'coord'=> [{random.randint(0, 120)}, {random.randint(0, 60)}], 'reason'=> '{random.choice(['BIT_FLIP', 'SKIP', 'REF_MISS'])}'}}]"
                    else:
                        err_data = "[]"
                
                # 破坏性格式：将 JSON 的 ':' 替换为 '=>'，强迫 Agent 进行字符串替换才能用 ast 验证或进行正规解析
                struct_dump = f"""C_STRUCT_DUMP:: 
{{
    'layer_stack'=> {{
        'vcl_nalu'=> {{
            'slice_type'=> '{pkt_type[0]}',
            'qp_val'=> {random.randint(20, 40)},
            'macroblock_errors'=> {err_data},
            'fatal_flag'=> {'True' if is_target else 'False'}
        }}
    }}
}}"""
                fm.write(struct_dump + "\n")
                fm.write(f"@@FRAME_END_MARKER\n\n")

if __name__ == "__main__":
    build_env()
