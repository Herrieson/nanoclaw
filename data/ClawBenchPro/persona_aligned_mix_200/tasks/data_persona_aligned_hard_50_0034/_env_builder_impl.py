import os
import json
import random
import time

def build_env():
    # 创建目录树
    os.makedirs("traces/deopt", exist_ok=True)
    os.makedirs("traces/gc", exist_ok=True)
    os.makedirs("src_map/namespaces", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    base_time = 1710000000.0  # 基准时间戳
    
    # ==========================================
    # 1. 生成 AST 映射文件 (高度碎片化与嵌套)
    # ==========================================
    for ns_id in range(20):
        os.makedirs(f"src_map/namespaces/ns_{ns_id}", exist_ok=True)
        
    def write_script_json(script_id, source_loc, symbol_name):
        ns_folder = f"ns_{script_id % 20}"
        filepath = f"src_map/namespaces/{ns_folder}/script_{script_id}.json"
        
        # 故意制造嵌套层级深的 JSON 结构
        data = {
            "v8_virtual_machine": {
                "isolate_ref": f"0x{random.randint(0x10000, 0xFFFFF):x}",
                "script_data": {
                    "compiled": True,
                    "ast_node": {
                        "metadata": {
                            "source_location": source_loc,
                            "symbol": symbol_name
                        }
                    }
                }
            }
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # 生成 2000 个干扰项映射
    for i in range(1000, 3000):
        if i not in (1337, 8888):  # 保留特殊 ID
            write_script_json(i, f"/app/node_modules/random_lib/chunk_{i}.js", f"anonymous_thunk_{i}")
            
    # 【真实罪魁祸首】 script_id: 1337
    write_script_json(1337, "/app/src/core/hot_path_router.js", "processRequestFastPath")
    # 【诱饵罪魁祸首】 script_id: 8888
    write_script_json(8888, "/app/node_modules/lodash/internal/map_fast.js", "map_fast_polyfill")

    # ==========================================
    # 2. 生成带时间线的混合日志事件 (噪音与多级逻辑)
    # ==========================================
    log_events = []
    
    # 诱饵风暴 (发生在 T + 1000 ~ 2000) - 总量极大 (3000条)
    for _ in range(3000):
        ts = base_time + random.uniform(1000.0, 2000.0)
        mem = f"{random.randint(0x1000000, 0x7FFFFFF):x}"
        log_events.append((ts, f"[{ts:.6f}] [v8::isolate] [bailout] <0x{mem}> id: 8888 | reason: 'wrong map' | deopt_id: {random.randint(1,99)} | type: soft"))

    # 真实故障风暴 (发生在 T + 8000 ~ 8499) - 总量较少 (1500条)，紧贴大 GC 前夕
    for _ in range(1500):
        ts = base_time + random.uniform(8000.0, 8499.0)
        mem = f"{random.randint(0x1000000, 0x7FFFFFF):x}"
        log_events.append((ts, f"[{ts:.6f}] [v8::isolate] [bailout] <0x{mem}> id: 1337 | reason: 'type feedback insufficient' | deopt_id: {random.randint(1,99)} | type: hard"))

    # 随机背景噪音与普通 bailout
    reasons = ["out of bounds", "not a function", "minus zero", "expected heap object"]
    for _ in range(5000):
        ts = base_time + random.uniform(0.0, 10000.0)
        rand_val = random.random()
        if rand_val < 0.2:
            # 纯十六进制干扰
            hex_dump = " ".join([f"{random.randint(0, 255):02x}" for _ in range(8)])
            log_events.append((ts, f"[{ts:.6f}] MEM_DUMP 0x{random.randint(0x1000, 0x7FFF):x}: {hex_dump} ...<core>..."))
        elif rand_val < 0.4:
            # TurboFan 编译信息
            log_events.append((ts, f"[{ts:.6f}] [TurboFan] Optimizing function 0x{random.randint(0x100, 0x9FF):x} (mode: OSR) ..."))
        else:
            # 随机无关函数的 bailout
            func_id = random.randint(1000, 2999)
            reason = random.choice(reasons)
            mem = f"{random.randint(0x1000000, 0x7FFFFFF):x}"
            log_events.append((ts, f"[{ts:.6f}] [v8::isolate] [bailout] <0x{mem}> id: {func_id} | reason: '{reason}' | deopt_id: {random.randint(1,99)} | type: soft"))

    # 按时间排序事件，以模拟真实日志追加
    log_events.sort(key=lambda x: x[0])
    
    # 切片写入到多个滚动日志中，强迫 Agent 遍历目录
    chunk_size = len(log_events) // 5
    for chunk_idx in range(5):
        chunk_lines = log_events[chunk_idx * chunk_size : (chunk_idx + 1) * chunk_size]
        with open(f"traces/deopt/v8_deopt_part_{chunk_idx}.log", "w", encoding="utf-8") as f:
            f.write(f"=== DEOPT TRACE LOG PART {chunk_idx} ===\n")
            for ts, line in chunk_lines:
                f.write(line + "\n")

    # ==========================================
    # 3. 构造关键线索：GC 停顿日志 (带有 5000ms+ 的唯一悬崖)
    # ==========================================
    gc_events = []
    # 正常 GC 事件
    for _ in range(100):
        ts = base_time + random.uniform(10.0, 9900.0)
        pause = random.uniform(1.0, 50.0)
        gc_type = "Scavenge" if random.random() > 0.3 else "Mark-Sweep"
        gc_events.append((ts, f"{ts:.3f} | {gc_type} | {pause:.2f} | {random.randint(100, 5000)}"))
        
    # 致命悬崖 (P99飙升的源头，设定在 T + 8505.0) -> 此时真实元凶刚风暴完
    fatal_ts = base_time + 8505.123
    gc_events.append((fatal_ts, f"{fatal_ts:.3f} | Mark-Sweep-Compact | 5402.88 | 12"))
    
    gc_events.sort(key=lambda x: x[0])
    
    with open("traces/gc/gc_events.log", "w", encoding="utf-8") as f:
        f.write("TIMESTAMP | GC_TYPE | DURATION_MS | FREED_KB\n")
        f.write("--------------------------------------------------\n")
        for ts, line in gc_events:
            f.write(line + "\n")

if __name__ == "__main__":
    build_env()
