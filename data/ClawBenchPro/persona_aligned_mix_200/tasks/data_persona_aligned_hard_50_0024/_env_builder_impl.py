import os
import json
import random
import string
import uuid
from datetime import datetime, timedelta

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_noise_logs(log_dir, start_time, num_chunks, is_failed=False, fail_reason="network"):
    for i in range(num_chunks):
        chunk_path = os.path.join(log_dir, f"stream_{i:04d}_{generate_random_string(6)}.log")
        with open(chunk_path, "w", encoding="utf-8") as f:
            for j in range(20):
                t = start_time + timedelta(seconds=i*10 + j*0.5)
                f.write(f"[{t.isoformat()}] [INFO] [System] Routine check {generate_random_string(8)} passed.\n")
                f.write(f"[{t.isoformat()}] [DEBUG] [Mem] Allocation trace: 0x{os.urandom(4).hex().upper()} OK\n")
            
            if is_failed and i == num_chunks - 1:
                t = start_time + timedelta(seconds=i*10 + 20)
                if fail_reason == "network":
                    f.write(f"[{t.isoformat()}] [FATAL] [Network] Connection timed out to registry.internal.net.\n")
                    f.write(f"[{t.isoformat()}] [ERROR] Job failed due to fetch error.\n")
                elif fail_reason == "disk":
                    f.write(f"[{t.isoformat()}] [FATAL] [IO] No space left on device while writing artifacts.\n")
                    f.write(f"[{t.isoformat()}] [ERROR] Job failed.\n")

def create_noise_pip_cache(cache_dir, num_files):
    for i in range(num_files):
        file_name = f"resolve_{uuid.uuid4().hex[:12]}.json"
        cache_data = {}
        for _ in range(random.randint(2, 5)):
            pkg_name = f"lib-{generate_random_string(5)}-util"
            cache_data[pkg_name] = {
                "resolved_version": f"{random.randint(0,3)}.{random.randint(0,20)}.{random.randint(0,9)}",
                "source": "public_pypi"
            }
        with open(os.path.join(cache_dir, file_name), "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)

def build_env():
    base_dir = "ci_pipelines"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("hotfix", exist_ok=True)
    
    nodes = ["Node-01", "Node-02", "Node-03", "Node-04", "Node-05"]
    branches = ["main", "dev", "feature/auth", "feature/ml-infer", "hotfix/ui"]
    statuses = ["success", "failed", "running"]
    
    # Generate 150 decoy jobs
    target_job_id = None
    
    for _ in range(150):
        job_id = f"job_{random.randint(10000, 99999)}"
        job_dir = os.path.join(base_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Ensure only ONE job is main + Node-03 + failed
        node = random.choice(nodes)
        branch = random.choice(branches)
        status = random.choice(statuses)
        
        if branch == "main" and node == "Node-03" and status == "failed":
            if target_job_id is None:
                target_job_id = job_id
            else:
                branch = "dev" # Change to avoid duplicate target
                
        if target_job_id is None and _ == 149:
            # Force target creation if not randomly created
            job_id = f"job_88492"
            job_dir = os.path.join(base_dir, job_id)
            os.makedirs(job_dir, exist_ok=True)
            node = "Node-03"
            branch = "main"
            status = "failed"
            target_job_id = job_id
            
        with open(os.path.join(job_dir, "meta.yaml"), "w", encoding="utf-8") as f:
            f.write(f"job_id: {job_id}\n")
            f.write(f"trigger_branch: {branch}\n")
            f.write(f"execution_node: {node}\n")
            f.write(f"status: {status}\n")
            f.write(f"timestamp: {datetime.now().isoformat()}\n")
            
        log_dir = os.path.join(job_dir, "logs")
        pip_dir = os.path.join(job_dir, "pip_cache")
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(pip_dir, exist_ok=True)
        
        start_time = datetime(2023, 11, 10, 10, 0, 0)
        
        if job_id == target_job_id:
            # The REAL crash scene
            # 1. Logs
            create_noise_logs(log_dir, start_time, 20)
            
            # CMake fragment (Clue: system_version)
            cmake_chunk = os.path.join(log_dir, f"stream_0021_cmake.log")
            with open(cmake_chunk, "w", encoding="utf-8") as f:
                t = start_time + timedelta(seconds=210)
                f.write(f"[{t.isoformat()}] [INFO] [CMake] -- Found Python3: /usr/bin/python3.9\n")
                f.write(f"[{t.isoformat()}] [INFO] [CMake] -- Found Boost: /usr/lib/x86_64-linux-gnu/cmake/Boost-1.74.0/BoostConfig.cmake (found version \"1.74.0\")\n")
                f.write(f"[{t.isoformat()}] [INFO] [CMake] -- Configuring done.\n")
            
            create_noise_logs(log_dir, start_time + timedelta(seconds=250), 10)
            
            # Make crash fragment (Clue: mismatch info & bad_version hint)
            make_chunk = os.path.join(log_dir, f"stream_0035_make_err.log")
            with open(make_chunk, "w", encoding="utf-8") as f:
                t = start_time + timedelta(seconds=350)
                f.write(f"[{t.isoformat()}] [ERROR] [Make] In file included from /opt/venv/lib/python3.9/site-packages/core_boost_python_wheels/include/boost/variant.hpp:14,\n")
                f.write(f"[{t.isoformat()}] [ERROR] [Make]                  from /workspace/src/pybind_wrapper/engine_export.cpp:42:\n")
                f.write(f"[{t.isoformat()}] [ERROR] [Make] /opt/venv/lib/python3.9/site-packages/core_boost_python_wheels/include/boost/variant/variant.hpp:1422: error: static assertion failed: Boost.Variant mismatch with system headers.\n")
                f.write(f"[{t.isoformat()}] [FATAL] [Make] Previous declaration was at /usr/include/boost/version.hpp:14 (Boost 1.74.0 detected, but 1.81.0 headers injected by python environment).\n")
                f.write(f"[{t.isoformat()}] [FATAL] [Make] make[2]: *** [src/CMakeFiles/hybrid_engine.dir/pybind_wrapper/engine_export.cpp.o] Error 1\n")

            # 2. Pip Cache (Clue: conflict_pkg exact name)
            create_noise_pip_cache(pip_dir, 15)
            target_pip_json = os.path.join(pip_dir, f"resolve_{uuid.uuid4().hex[:12]}.json")
            with open(target_pip_json, "w", encoding="utf-8") as f:
                json.dump({
                    "numpy": {"resolved_version": "1.24.3", "source": "pypi"},
                    "core-boost-python-wheels": {
                        "resolved_version": "1.81.0",
                        "source": "internal_ml_registry",
                        "injected_by": "custom-ml-infer>=2.0"
                    },
                    "scipy": {"resolved_version": "1.10.1", "source": "pypi"}
                }, f, indent=2)

        else:
            # Decoy scenes
            if status == "success":
                create_noise_logs(log_dir, start_time, random.randint(10, 30))
            elif status == "failed":
                reason = random.choice(["network", "disk"])
                create_noise_logs(log_dir, start_time, random.randint(10, 30), is_failed=True, fail_reason=reason)
            else:
                create_noise_logs(log_dir, start_time, random.randint(5, 15))
            
            create_noise_pip_cache(pip_dir, random.randint(5, 10))

if __name__ == '__main__':
    build_env()
