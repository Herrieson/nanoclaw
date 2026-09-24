import os
import random
import datetime
import string

def generate_ansi_noise():
    colors = ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m', '\x1b[36m', '\x1b[0m']
    return random.choice(colors)

def generate_hex_dump():
    lines = []
    for _ in range(random.randint(5, 15)):
        addr = f"{random.randint(0, 0xFFFFFFFF):08x}"
        hex_data = " ".join([f"{random.randint(0, 255):02x}" for _ in range(16)])
        chars = "".join([random.choice(string.ascii_letters + string.digits + ".") for _ in range(16)])
        lines.append(f"{addr}  {hex_data}  |{chars}|")
    return "\n".join(lines)

def build_env():
    # Create necessary directories (do NOT create ci_patch, let the agent do it)
    os.makedirs("build_artifacts", exist_ok=True)
    
    start_time = datetime.datetime.now() - datetime.timedelta(hours=2)
    
    log_file_path = "build_artifacts/docker_build_runner_9942_raw.log"
    
    with open(log_file_path, "w", encoding="utf-8") as f:
        # 1. Generate massive Docker build noise (Layer pulls)
        for i in range(1000):
            ts = (start_time + datetime.timedelta(seconds=i)).isoformat() + "Z"
            hash_val = "".join(random.choices(string.hexdigits.lower(), k=64))
            f.write(f"{generate_ansi_noise()}[{ts}] Step 4/15 : Pulling fs layer {hash_val[:12]}\x1b[0m\n")
            if i % 100 == 0:
                f.write(f"[{ts}] Status: Downloaded newer image for registry.internal/base:latest\n")
        
        # 2. Generate C++ compilation warnings (Very noisy)
        for i in range(5000):
            ts = (start_time + datetime.timedelta(seconds=1000 + i*0.1)).isoformat() + "Z"
            f.write(f"{generate_ansi_noise()}[{ts}] [WARNING] /usr/include/c++/9/bits/stl_vector.h:1040: {random.choice(string.ascii_lowercase)}_var is uninitialized.\x1b[0m\n")
            if random.random() > 0.95:
                f.write(f"{generate_ansi_noise()}In file included from /src/core/math_operations.cpp:{random.randint(10,200)}:\x1b[0m\n")
                
        # 3. Insert fake fatal errors to distract
        f.write("\n[FATAL] [Thread-04] Unit Test `test_tensor_allocation` segfaulted. Core dump attached:\n")
        f.write(generate_hex_dump() + "\n")
        
        # 4. Generate the REAL dependency conflict error buried inside (Enhanced to hide package names behind Node IDs)
        ts_conflict = (start_time + datetime.timedelta(seconds=1600)).isoformat() + "Z"
        f.write(f"\n{generate_ansi_noise()}[{ts_conflict}] [INFO] Starting Spire Hybrid dependency resolution graph builder...\x1b[0m\n")
        f.write(f"{generate_ansi_noise()}[{ts_conflict}] [DEBUG] Scanning module_x, module_y, module_z...\x1b[0m\n")
        f.write(f"\x1b[31m[{ts_conflict}] [FATAL] [Thread-14] Dependency resolution failed for target 'hybrid-engine'.\x1b[0m\n")
        f.write(f"\x1b[31m[{ts_conflict}] [FATAL] [Thread-14] Conflict detected in transitive graph:\x1b[0m\n")
        f.write(f"\x1b[31m[{ts_conflict}] [FATAL] [Thread-14]   -> module_x/3.4.1@core/stable requires 'node_id: 8f3a9b2c'\x1b[0m\n")
        f.write(f"\x1b[31m[{ts_conflict}] [FATAL] [Thread-14]   -> module_y/1.2.0@core/stable requires 'node_id: 4e2d1f7a'\x1b[0m\n")
        f.write(f"\x1b[31m[{ts_conflict}] [FATAL] [Thread-14] Aborting build. Please resolve graph constraints before proceeding.\x1b[0m\n")
        
        # 5. More noise after the error
        for i in range(2000):
            ts = (start_time + datetime.timedelta(seconds=1601 + i*0.1)).isoformat() + "Z"
            f.write(f"[{ts}] [ERROR] Make command failed with exit code 2.\n")
            if i % 500 == 0:
                f.write(generate_hex_dump() + "\n")
                
    # Create a secondary misleading config file
    with open("build_artifacts/runner_env_dump.json", "w", encoding="utf-8") as f:
        f.write("""{
    "runner_id": "gh-runner-europe-9942",
    "labels": ["self-hosted", "linux", "x64", "gpu-enabled"],
    "env": {
        "PYTHON_VERSION": "3.10.12",
        "CMAKE_VERSION": "3.22.1",
        "PRE_INSTALLED_DEPS": {
            "eigen_matrix": "3.3.0",
            "boost": "1.74.0"
        }
    }
}""")

if __name__ == "__main__":
    build_env()
