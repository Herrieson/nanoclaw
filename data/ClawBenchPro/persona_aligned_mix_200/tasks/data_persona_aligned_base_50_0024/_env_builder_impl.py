import os
import json
import random
import string
from datetime import datetime, timedelta

def build_env():
    # 创建基础目录树结构
    os.makedirs("build_artifacts", exist_ok=True)
    os.makedirs("crash_reports", exist_ok=True)
    os.makedirs("hotfix", exist_ok=True)

    # 1. 生成极具迷惑性的海量 CI 日志 (包含标准输出、CMake检查、pip解析、编译堆栈)
    log_path = "build_artifacts/gitlab-job-88492.log"
    start_time = datetime(2023, 11, 10, 18, 0, 0)
    
    with open(log_path, "w", encoding="utf-8") as f:
        # 阶段一：环境准备与杂乱噪音
        for i in range(1500):
            hex_id = os.urandom(6).hex()
            f.write(f"[{start_time + timedelta(seconds=i*0.3)}] [INFO] [Docker] Layer {hex_id}: Pull complete\n")
        
        # 核心线索一：系统原本的基础版本
        f.write(f"[{start_time + timedelta(seconds=500)}] [INFO] [CMake] -- Found Python3: /usr/bin/python3.9 (found version \"3.9.2\") found components: Interpreter Development \n")
        f.write(f"[{start_time + timedelta(seconds=501)}] [INFO] [CMake] -- Found Boost: /usr/lib/x86_64-linux-gnu/cmake/Boost-1.74.0/BoostConfig.cmake (found version \"1.74.0\")\n")
        f.write(f"[{start_time + timedelta(seconds=502)}] [INFO] [CMake] -- Configuring done. Generating build system...\n")
        
        # 阶段二：Python 依赖解析与安装 (干扰项 + 真实的错误源头)
        for i in range(2500):
            pkg = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
            v_major = random.randint(0, 4)
            v_minor = random.randint(0, 20)
            f.write(f"[{start_time + timedelta(seconds=600+i*0.1)}] [INFO] [Pip] Collecting {pkg}=={v_major}.{v_minor}\n")
            if i % 100 == 0:
                f.write(f"[{start_time + timedelta(seconds=600+i*0.1)}] [WARN] [Pip] Requirement already satisfied: {pkg} in /usr/local/lib/python3.9/site-packages\n")

        # 核心线索二：冲突包的安装记录
        f.write(f"[{start_time + timedelta(seconds=850.1)}] [INFO] [Pip] Collecting boost-python-deps==1.81.0 (from custom-ml-infer>=2.0)\n")
        f.write(f"[{start_time + timedelta(seconds=850.2)}] [INFO] [Pip] Downloading boost_python_deps-1.81.0-cp39-cp39-manylinux_2_17_x86_64.whl (45.2 MB)\n")
        f.write(f"[{start_time + timedelta(seconds=855.0)}] [INFO] [Pip] Installing collected packages: boost-python-deps, custom-ml-infer\n")
        f.write(f"[{start_time + timedelta(seconds=860.0)}] [INFO] [Pip] Successfully installed boost-python-deps-1.81.0 custom-ml-infer-2.1.0\n")

        # 阶段三：C++ 正常编译过程噪音
        for i in range(4000):
            file_num = str(i).zfill(4)
            f.write(f"[{start_time + timedelta(seconds=900+i*0.15)}] [INFO] [Make] [ {i%100}%] Building CXX object src/CMakeFiles/hybrid_engine.dir/module_compute_{file_num}.cpp.o\n")
            if i % 50 == 0:
                f.write(f"[{start_time + timedelta(seconds=900+i*0.15)}] [WARN] [Make] src/module_compute_{file_num}.cpp:42:10: warning: unused variable 'temp_buffer' [-Wunused-variable]\n")

        # 核心线索三：编译崩溃现场
        crash_time = start_time + timedelta(seconds=1500)
        f.write(f"[{crash_time}] [ERROR] [Make] In file included from /opt/venv/lib/python3.9/site-packages/boost_python_deps/include/boost/variant.hpp:14,\n")
        f.write(f"[{crash_time}] [ERROR] [Make]                  from /workspace/src/pybind_wrapper/engine_export.cpp:42:\n")
        f.write(f"[{crash_time}] [ERROR] [Make] /opt/venv/lib/python3.9/site-packages/boost_python_deps/include/boost/variant/variant.hpp:1422: error: static assertion failed: Boost.Variant mismatch with system headers.\n")
        f.write(f"[{crash_time}] [FATAL] [Make] Previous declaration was at /usr/include/boost/version.hpp:14 (Boost 1.74.0 detected, but 1.81.0 headers injected by python environment).\n")
        f.write(f"[{crash_time}] [FATAL] [Make] make[2]: *** [src/CMakeFiles/hybrid_engine.dir/pybind_wrapper/engine_export.cpp.o] Error 1\n")
        
        # 阶段四：崩溃后的级联错误噪音
        for i in range(1500):
            f.write(f"[{crash_time + timedelta(seconds=i*0.05)}] [ERROR] [Make] make[1]: *** [src/CMakeFiles/hybrid_engine.dir/all] Error 2\n")

    # 2. 生成完全无用的 Hex Dump (制造陷阱与脏数据)
    with open("crash_reports/core_dump_traces.log", "w", encoding="utf-8") as f:
        f.write("=== FATAL SEGFAULT TRACE (SIGSEGV) ===\n")
        f.write("THREAD_ID: 0x00007FFA3B2C1000\n")
        f.write("REGISTERS:\n")
        f.write("RAX: 0x0000000000000000 RBX: 0x00007FFC9D1A2B30\n")
        f.write("MEMORY DUMP:\n")
        for _ in range(800):
            chunk = os.urandom(16).hex().upper()
            formatted_chunk = ' '.join(chunk[i:i+4] for i in range(0, 32, 4))
            f.write(f"0x{os.urandom(4).hex().upper().zfill(8)}: {formatted_chunk}\n")

    # 3. 生成深度嵌套的 JSON 文件 (依赖树，需跨文件佐证)
    def generate_deep_dict(depth, max_depth):
        if depth >= max_depth:
            return f"{random.randint(0, 5)}.{random.randint(0, 15)}.{random.randint(0, 9)}"
        return {
            ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 8))): generate_deep_dict(depth + 1, max_depth)
            for _ in range(random.randint(1, 4))
        }

    deps_tree = generate_deep_dict(0, 5)
    
    # 将真实的元凶埋入深度层级中
    deps_tree["ml_dependencies"] = {
        "perception_module": {
            "version": "1.4.2",
            "requires": generate_deep_dict(1, 3)
        },
        "custom-ml-infer": {
            "version": "2.1.0",
            "description": "Internal model inference wrapper",
            "requires": {
                "numpy": "1.24.3",
                "scipy": "1.10.1",
                "boost-python-deps": "1.81.0"
            }
        }
    }
    
    with open("build_artifacts/deps_tree.json", "w", encoding="utf-8") as f:
        json.dump(deps_tree, f, indent=4)

if __name__ == '__main__':
    build_env()
