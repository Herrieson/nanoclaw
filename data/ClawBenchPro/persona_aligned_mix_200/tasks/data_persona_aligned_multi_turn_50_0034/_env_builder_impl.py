import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("raw_traces", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("analysis_reports", exist_ok=True)

    # 埋点限制条件（Agent需要在T1记住这些，T2/T3不能直接被提示词告知）
    limits = {
        "sre_thresholds": {
            "max_deopt_loops": 4,
            "max_cumulative_gc_pause_ms": 120.0
        }
    }
    with open("config/engine_limits.json", "w") as f:
        json.dump(limits, f, indent=4)

    # 模拟 V8 混合日志
    # 陷阱1： render_ui 去优化了，但次数不够（3次）。
    # 陷阱2： parse_json_payload GC耗时很大，但没有去优化。
    # 真实目标： process_order_pipeline，去优化5次，且GC累计超过120ms。
    log_content = """[1001.01] [optimize] process_order_pipeline (target: TurboFan)
[1001.05] [scavenge] GC 12.5ms (from 24MB to 18MB)
[1002.10] [deoptimize] process_order_pipeline - reason: insufficient type feedback for call
[1002.15] [mark-sweep] GC 45.2ms (from 50MB to 20MB)
[1003.00] [optimize] render_ui (target: TurboFan)
[1004.22] [deoptimize] render_ui - reason: map check failed
[1005.01] [optimize] process_order_pipeline (target: TurboFan)
[1006.11] [deoptimize] process_order_pipeline - reason: polymorphic IC
[1006.12] [scavenge] GC 33.1ms
[1007.00] [optimize] render_ui (target: TurboFan)
[1007.50] [deoptimize] render_ui - reason: map check failed
[1008.00] [optimize] parse_json_payload (target: TurboFan)
[1008.50] [mark-sweep] GC 150.0ms (from 120MB to 40MB)
[1009.00] [optimize] process_order_pipeline (target: TurboFan)
[1009.10] [deoptimize] process_order_pipeline - reason: uninitialized symbol
[1009.20] [mark-sweep] GC 55.4ms
[1010.00] [optimize] process_order_pipeline (target: TurboFan)
[1010.15] [deoptimize] process_order_pipeline - reason: unexpected map
[1010.50] [scavenge] GC 10.0ms
[1011.00] [optimize] render_ui (target: TurboFan)
[1011.50] [deoptimize] render_ui - reason: map check failed
[1012.00] [optimize] process_order_pipeline (target: TurboFan)
[1012.50] [deoptimize] process_order_pipeline - reason: polymorphic IC
"""
    with open("raw_traces/isolate-0x123abc.log", "w") as f:
        f.write(log_content)

def build_turn_2():
    os.makedirs("new_traces", exist_ok=True)
    
    # T2日志：process_order_pipeline 被修复了，不再deopt。
    # 新生代目标： calculate_discount_rules 疯狂 bailout。
    log_content = """[2001.01] [optimize] process_order_pipeline (target: TurboFan)
[2001.05] [scavenge] GC 5.0ms
[2002.00] [optimize] calculate_discount_rules (target: TurboFan)
[2002.10] [deoptimize] calculate_discount_rules - reason: wrong map
[2003.00] [optimize] calculate_discount_rules (target: TurboFan)
[2003.10] [deoptimize] calculate_discount_rules - reason: wrong map
[2004.00] [optimize] calculate_discount_rules (target: TurboFan)
[2004.10] [deoptimize] calculate_discount_rules - reason: wrong map
[2005.00] [optimize] calculate_discount_rules (target: TurboFan)
[2005.10] [deoptimize] calculate_discount_rules - reason: wrong map
[2006.00] [optimize] calculate_discount_rules (target: TurboFan)
[2006.10] [deoptimize] calculate_discount_rules - reason: wrong map
[2007.00] [optimize] render_ui (target: TurboFan)
[2007.50] [deoptimize] render_ui - reason: bounds check
"""
    with open("new_traces/isolate-0x999def.log", "w") as f:
        f.write(log_content)

def build_turn_3():
    os.makedirs("dumps", exist_ok=True)
    
    # T3 堆快照：需要结合前两轮的记忆。
    # 阈值：T1记录的GC红线是 120.0，所以这里我们要找 Retained_Size_MB > 120.0 且在嫌疑名单里的函数。
    # 目标： calculate_discount_rules (185.5 MB) -> T2嫌疑犯
    # process_order_pipeline (45.2 MB) -> T1嫌疑犯，但没超过120
    # memory_hog_func (300.0 MB) -> 陷阱，超标了但不在嫌疑名单里
    
    csv_data = [
        ["Function_Context", "Self_Size_MB", "Retained_Size_MB", "Instance_Count"],
        ["process_order_pipeline", "5.0", "45.2", "12000"],
        ["calculate_discount_rules", "12.5", "185.5", "500000"],
        ["memory_hog_func", "50.0", "300.0", "10000"],
        ["render_ui", "2.1", "15.0", "300"],
        ["parse_json_payload", "1.0", "8.0", "50"]
    ]
    
    with open("dumps/heap_retained.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

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
