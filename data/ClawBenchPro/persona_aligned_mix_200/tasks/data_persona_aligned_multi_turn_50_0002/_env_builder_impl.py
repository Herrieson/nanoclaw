import os
import argparse
import json

def build_turn_1():
    # === 构建项目源码配置 ===
    os.makedirs("project_src/auth_service", exist_ok=True)
    os.makedirs("project_src/data_processor", exist_ok=True)
    os.makedirs("project_src/core_engine", exist_ok=True)
    
    with open("project_src/auth_service/requirements.txt", "w") as f:
        f.write("flask>=2.0.0\nPyJWT==2.4.0\ncryptography>=38.0.0\n")

    with open("project_src/data_processor/requirements.txt", "w") as f:
        # 陷阱：复杂的三角依赖
        # numba < 0.57.0 强依赖 numpy < 1.24.0 (即最大1.23.5)
        # scipy >= 1.10.0 依赖 numpy >= 1.23.5
        # 所以必须选定 numpy == 1.23.5
        f.write("pandas<2.0.0\nnumpy\nnumba<0.57.0\nscipy>=1.10.0\npyarrow==10.0.1\n")

    with open("project_src/core_engine/CMakeLists.txt", "w") as f:
        # 陷阱：C++ 依赖
        # 基础镜像提供的是 1.74.0, 这里强制要求 1.78.0
        # 如果升到 >=1.82.0，会导致后续 pybind11 出错 (在日志中体现)
        f.write("""cmake_minimum_required(VERSION 3.14)
project(KrakenCore)
find_package(Boost 1.78.0 REQUIRED COMPONENTS system thread)
find_package(pybind11 REQUIRED)
add_library(core_engine SHARED src/main.cpp)
target_link_libraries(core_engine PRIVATE Boost::system Boost::thread pybind11::module)
""")

    # === 构建虚假的 CI 庞大日志 ===
    os.makedirs("ci_logs/auth_service", exist_ok=True)
    os.makedirs("ci_logs/data_processor", exist_ok=True)
    os.makedirs("ci_logs/core_engine", exist_ok=True)

    # 填充大量干扰日志
    for svc in ["auth_service", "data_processor", "core_engine"]:
        for i in range(1, 10):
            with open(f"ci_logs/{svc}/build_worker_{i:02d}.log", "w") as f:
                f.write(f"[INFO] Initializing environment on runner {i}...\n")
                f.write(f"[INFO] Fetching submodules...\n")
                f.write(f"[INFO] Done fetching submodules.\n")

    # 注入关键的错误日志
    with open("ci_logs/core_engine/build_worker_03_critical.log", "w") as f:
        f.write("""[INFO] Running CMake step...
[INFO] CXX compiler: /usr/bin/c++
-- Found pybind11: /usr/local/include (found version "2.10.0" )
CMake Error at CMakeLists.txt:4 (find_package):
  Could NOT find Boost (missing: system thread) (Required is at least version "1.78.0").
  Found version "1.74.0".
  
  [HINT] Do not upgrade Boost to 1.82.0 or above, as it breaks compatibility with the current pybind11 2.10.0 headers due to deprecated BOOST_BIND macros.
-- Configuring incomplete, errors occurred!
""")

    with open("ci_logs/data_processor/build_worker_12_critical.log", "w") as f:
        f.write("""[INFO] Running pip install -r requirements.txt...
Collecting pandas<2.0.0
  Downloading pandas-1.5.3.tar.gz
Collecting numpy
  Downloading numpy-1.24.2.tar.gz
Collecting numba<0.57.0
  Downloading numba-0.56.4.tar.gz
Collecting scipy>=1.10.0
  Downloading scipy-1.10.1.tar.gz
ERROR: Cannot install numba<0.57.0 and numpy==1.24.2 because these package versions have conflicting dependencies.
The conflict is caused by:
    The user requested numpy
    numba 0.56.4 depends on numpy<1.24,>=1.18
To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip attempt to solve the dependency conflict
[FATAL] Build failed with exit code 1.
""")

def build_turn_2():
    # 模拟 turn_2：在已有的基础增加 CVE 漏洞扫描报告
    os.makedirs("security", exist_ok=True)
    
    # 构建陷阱：
    # 上一轮中合理推导： numpy 只能是 1.23.5。Boost 只能是 1.78 ~ 1.81。
    # 这一轮： numpy 1.23.5 被拉黑。
    # 为了解决 numpy 1.23.5 拉黑，必须升级 numpy >= 1.24.3。
    # 但这打破了 numba < 0.57.0 的限制。所以必须违背 requirements.txt 中 numba 的旧锁定，
    # 强制将 numba 升级到 0.57.1 (兼容 numpy 1.24+)，并且由于连锁反应，scipy 也得用兼容版本。
    # Boost 1.78 ~ 1.79 爆出严重内存泄漏 CVE。必须逼迫升级到 1.80.0 或 1.81.0。
    
    cve_data = {
        "scan_target": "kraken_pipeline",
        "timestamp": "2023-11-20T10:00:00Z",
        "critical_vulnerabilities": [
            {
                "cve_id": "CVE-2023-NUMPY-01",
                "component": "numpy",
                "affected_versions": "<= 1.24.2",
                "resolution": "Upgrade to >= 1.24.3",
                "severity": "CRITICAL"
            },
            {
                "cve_id": "CVE-2023-BOOST-44",
                "component": "Boost",
                "affected_versions": "< 1.80.0",
                "resolution": "Upgrade to >= 1.80.0",
                "severity": "HIGH"
            },
            {
                "cve_id": "CVE-2023-PYJWT-99",
                "component": "PyJWT",
                "affected_versions": "== 2.4.0",
                "resolution": "Upgrade to 2.8.0",
                "severity": "MEDIUM"
            }
        ]
    }
    
    with open("security/cve_bulletins_2023_Q4.json", "w") as f:
        json.dump(cve_data, f, indent=4)

def build_turn_3():
    # 模拟 turn_3：产物体积超标告警和单阶段 Dockerfile 暴露
    os.makedirs("ci_metrics", exist_ok=True)
    with open("ci_metrics/docker_dive_report.txt", "w") as f:
        f.write("""================ DIVE IMAGE ANALYSIS ================
Image: kraken_system:latest
Total Image Size: 3.2 GB
Potential Wasted Space: 2.4 GB

Layer 1: 150 MB (Base OS)
Layer 2: 1.8 GB (apt-get install build-essential gcc g++ wget cmake libboost-all-dev python3-dev) 
  -> [WARN] Contains 800MB in /usr/local/include/boost
  -> [WARN] Contains 400MB in /var/lib/apt/lists
Layer 3: 1.1 GB (pip install -r requirements.txt && python setup.py bdist_wheel)
  -> [WARN] Contains 500MB in ~/.cache/pip
Layer 4: 150 MB (Compiled binaries and python site-packages)

[SUGGESTION] Dev tools, header files, and build caches should not be present in the final production layer.
=====================================================
""")

    # 提供单阶段构建的臃肿 Dockerfile
    auth_dockerfile = """FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
"""
    data_dockerfile = """FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential gcc g++ cmake
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "worker.py"]
"""
    core_dockerfile = """FROM ubuntu:22.04
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential cmake python3 python3-pip python3-dev wget
# Installing Boost from source
RUN wget https://boostorg.jfrog.io/artifactory/main/release/1.80.0/source/boost_1_80_0.tar.gz && \
    tar -xzf boost_1_80_0.tar.gz && cd boost_1_80_0 && ./bootstrap.sh && ./b2 install
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY CMakeLists.txt .
COPY src/ ./src/
RUN cmake . && make
CMD ["./core_engine"]
"""
    with open("project_src/auth_service/Dockerfile.production", "w") as f:
        f.write(auth_dockerfile)
    with open("project_src/data_processor/Dockerfile.production", "w") as f:
        f.write(data_dockerfile)
    with open("project_src/core_engine/Dockerfile.production", "w") as f:
        f.write(core_dockerfile)

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
