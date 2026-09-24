import os
import json

def build_env():
    # 创建基础目录树结构
    os.makedirs("crash_reports", exist_ok=True)
    os.makedirs("hotfix", exist_ok=True)

    # 1. 生成崩溃现场摘要 (移除明文日志，仅保留残影，迫使 Agent 使用 Skill)
    crash_summary = {
        "event_id": "err-9943-abcf",
        "timestamp": "2023-11-10T18:25:00Z",
        "node": "Node-03",
        "job_id": 88492,
        "fatal_error": "make[2]: *** [src/CMakeFiles/hybrid_engine.dir/pybind_wrapper/engine_export.cpp.o] Error 1",
        "compiler_traceback": [
            "In file included from /opt/venv/lib/python3.9/site-packages/boost_python_deps/include/boost/variant.hpp:14,",
            "                 from /workspace/src/pybind_wrapper/engine_export.cpp:42:",
            "/opt/venv/lib/python3.9/site-packages/boost_python_deps/include/boost/variant/variant.hpp:1422: error: static assertion failed: Boost.Variant mismatch with system headers.",
            "[FATAL] Previous declaration was at /usr/include/boost/version.hpp:14 (System Boost detected, but high-version headers injected by python environment)."
        ],
        "note": "Full stdout logs were truncated due to container kernel panic. Please refer to external log sinks."
    }
    
    with open("crash_reports/crash_summary.json", "w", encoding="utf-8") as f:
        json.dump(crash_summary, f, indent=4)

    # 2. 生成完全无用的 Hex Dump (保留原有的脏数据陷阱)
    with open("crash_reports/core_dump_traces.log", "w", encoding="utf-8") as f:
        f.write("=== FATAL SEGFAULT TRACE (SIGSEGV) ===\n")
        f.write("THREAD_ID: 0x00007FFA3B2C1000\n")
        f.write("REGISTERS:\n")
        f.write("RAX: 0x0000000000000000 RBX: 0x00007FFC9D1A2B30\n")
        f.write("MEMORY DUMP:\n")
        for _ in range(200):
            chunk = os.urandom(16).hex().upper()
            formatted_chunk = ' '.join(chunk[i:i+4] for i in range(0, 32, 4))
            f.write(f"0x{os.urandom(4).hex().upper().zfill(8)}: {formatted_chunk}\n")

if __name__ == '__main__':
    build_env()
