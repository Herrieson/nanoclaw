import os
import json
import random
import time

def build_env():
    # 创建所有需要的相对路径目录
    os.makedirs("traces", exist_ok=True)
    os.makedirs("src_map", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    # 1. 构造深层嵌套、且带有迷惑性的 AST 映射表 src_map/scripts.json
    scripts_data = {
        "v8_virtual_machine": {
            "instances": {
                "isolate_0x7f8a9b22c000": {
                    "heap_snapshot_ref": "invalid",
                    "execution_context": {
                        "loaded_scripts": {}
                    }
                }
            }
        }
    }
    
    target_scripts_node = scripts_data["v8_virtual_machine"]["instances"]["isolate_0x7f8a9b22c000"]["execution_context"]["loaded_scripts"]

    # 写入干扰项脚本
    for i in range(1000, 1050):
        target_scripts_node[str(i)] = {
            "compiled": True,
            "ast_root": {
                "metadata": {
                    "source_loc": f"/app/node_modules/lodash/internal/func_{i}.js",
                    "symbol_name": f"anonymous_thunk_{i}"
                }
            }
        }
    
    # 写入真实罪魁祸首的脚本信息 (ID: 1024)
    target_scripts_node["1024"] = {
        "compiled": True,
        "ast_root": {
            "metadata": {
                "source_loc": "/app/src/core/hot_path_router.js",
                "symbol_name": "processRequestFastPath"
            }
        }
    }

    with open("src_map/scripts.json", "w", encoding="utf-8") as f:
        json.dump(scripts_data, f, indent=2)

    # 2. 构造极其非标准的、混杂十六进制乱码的 V8 去优化日志 traces/v8_deopt.log
    reasons = [
        "insufficient type feedback for call",
        "out of bounds",
        "not a function",
        "minus zero",
        "wrong map",
        "expected heap object"
    ]
    
    with open("traces/v8_deopt.log", "w", encoding="utf-8") as f:
        f.write("=== V8 JIT DEOPTIMIZATION TRACE START ===\n")
        f.write("V8 version 9.4.146.24\n")
        f.write("Flags: --trace-deopt --trace-compiler --trace-ic\n\n")
        
        base_time = time.time() - 3600
        
        for _ in range(500):
            rand_val = random.random()
            if rand_val < 0.15:
                # 纯粹的十六进制内存 dump 干扰噪音
                hex_dump = " ".join([f"{random.randint(0, 255):02x}" for _ in range(16)])
                f.write(f"0x{random.randint(0x10000000, 0x7FFFFFFF):x}: {hex_dump}  ...<core_dump>...\n")
            elif rand_val < 0.30:
                # TurboFan 编译优化日志干扰
                f.write(f"[TurboFan] Optimizing function 0x{random.randint(0x100000, 0x9FFFFF):x} (mode: OSR) ...\n")
            else:
                # 真实的 bailout 事件
                is_culprit = random.random() < 0.85 # 罪魁祸首霸屏 (85%概率)
                func_id = "1024" if is_culprit else str(random.randint(1000, 1049))
                reason = "wrong map" if is_culprit else random.choice(reasons)
                
                ts = base_time + random.uniform(0.1, 3500.0)
                mem_addr = f"0x{random.randint(0x100000000000, 0x7FFFFFFFFFFF):x}"
                
                # 非标准的日志分隔符和格式
                f.write(f"[{ts:.6f}] [bailout] <{mem_addr}> id: {func_id} | reason: '{reason}' | deopt_id: {random.randint(1, 100)} | type: soft\n")

    # 3. 构造 GC 停顿日志，增加场景真实感
    with open("traces/gc_pauses.log", "w", encoding="utf-8") as f:
        f.write("## GC PAUSE METRICS ##\n")
        f.write("TIMESTAMP || TYPE || PAUSE_DURATION_MS || MEM_FREED_KB\n")
        
        for _ in range(30):
            ts = base_time + random.uniform(10.0, 3000.0)
            gc_type = "Scavenge" if random.random() > 0.2 else "Mark-Sweep"
            pause = random.uniform(0.5, 12.0)
            freed = random.randint(100, 5000)
            f.write(f"{ts:.3f} || {gc_type} || {pause:.2f} || {freed}\n")
            
        # 结尾处巨大的性能悬崖
        f.write(f"{base_time + 3550.123:.3f} || Mark-Sweep || 5402.88 || 12\n")
        f.write(f"{base_time + 3555.456:.3f} || Mark-Sweep || 6120.45 || 8\n")
        f.write("! WARNING: HEAP NEARING LIMIT !\n")

if __name__ == "__main__":
    build_env()
