import os
import csv
import json
import random
import string
import re

def generate_ansi_garbage_log(lines=150, is_fatal=False, fatal_lib="", fatal_actual=""):
    log = []
    ansi_colors = ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m', '\x1b[35m', '\x1b[36m', '\x1b[90m', '\x1b[1m', '\x1b[0m']
    
    for i in range(lines):
        ts = f"[2023-10-27T03:14:{random.randint(10,59)}.{random.randint(100,999)}Z]"
        color_1 = random.choice(ansi_colors)
        color_2 = random.choice(ansi_colors)
        reset = '\x1b[0m'
        
        chance = random.random()
        if chance > 0.95:
            # Hex dump garbage
            garbage = "".join(random.choices(string.hexdigits, k=64))
            log.append(f"{ts} {color_1}[DEBUG] core dump trace: 0x{garbage}{reset}")
        elif chance > 0.85:
            # Fake compiler warnings
            log.append(f"{ts} {color_2}warning:{reset} unused parameter 'ctx_{i}' [-Wunused-parameter]")
            log.append(f"{ts} {color_1}  12 | void process(int ctx_{i}) {{{reset}")
        else:
            # Normal build progress
            log.append(f"{ts} {color_1}[{random.randint(1,100)}%] Building CXX object CMakeFiles/module_{random.randint(1,999)}.cpp.o{reset}")

    if is_fatal:
        fatal_idx = int(lines * 0.7)
        ts = "[2023-10-27T03:14:45.123Z]"
        
        # Obfuscated fatal error with ANSI codes mixed into words
        error_msg = (
            f"{ts} \x1b[31mFAILED:\x1b[0m src/CMakeFiles/core.dir/crypto_module.cpp.o\n"
            f"{ts} \x1b[1m/usr/src/app/vendor/includes/abi_check.h:42:2:\x1b[0m "
            f"\x1b[31mfatal error:\x1b[0m static assertion failed: \"\x1b[1mABI check failed\x1b[0m for "
            f"\x1b[35m{fatal_lib}\x1b[0m! Loaded rogue headers for version \x1b[31m{fatal_actual}\x1b[0m. Please check the sysroot.\"\n"
            f"{ts}  42 | #error \"ABI mismatch detected\"\n"
            f"{ts}     |  ^~~~~\n"
            f"{ts} 1 error generated.\n"
            f"{ts} ninja: build stopped: subcommand failed."
        )
        log.insert(fatal_idx, error_msg)

    return "\n".join(log)

def build_env():
    # Directories
    os.makedirs("ci_system", exist_ok=True)
    os.makedirs("repo/build_settings/manifests", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    
    pools = ["alpha", "beta", "gamma", "delta", "epsilon"]
    for p in pools:
        os.makedirs(f"ci_logs/node_pool_{p}", exist_ok=True)

    # 1. Generate Metadata CSV
    pipelines = []
    target_pipeline = 8992
    target_commit = "a7f9b2c8"
    target_pool = "gamma"
    target_lib = "lib_crypto_vault"
    expected_version = "3.0.5"
    actual_version = "2.1.0"

    for i in range(8800, 9000):
        commit = "".join(random.choices(string.hexdigits.lower(), k=8))
        pool = random.choice(pools)
        status = "SUCCESS"
        if i == target_pipeline:
            commit = target_commit
            pool = target_pool
            status = "FAILED"
        elif random.random() > 0.9:
            status = "FAILED"
        
        pipelines.append({
            "pipeline_id": i,
            "commit_hash": commit,
            "status": status,
            "node_pool": f"node_pool_{pool}"
        })

    with open("ci_system/run_meta.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["pipeline_id", "commit_hash", "status", "node_pool"])
        writer.writeheader()
        writer.writerows(pipelines)

    # 2. Generate JSON Manifests
    for p in pipelines:
        commit = p["commit_hash"]
        manifest = {
            "metadata": {
                "commit": commit,
                "author": "bot",
            },
            "dependencies": {
                "boost": {"locked_version": "1.82.0"},
                "fmtlib": {"locked_version": f"9.{random.randint(0,2)}.{random.randint(0,5)}"},
                "spdlog": {"locked_version": "1.11.0"},
            }
        }
        
        if commit == target_commit:
            manifest["dependencies"][target_lib] = {"locked_version": expected_version}
        else:
            # Add distractor libs
            if random.random() > 0.5:
                manifest["dependencies"]["lib_crypto_vault"] = {"locked_version": f"3.0.{random.randint(1,4)}"}
            if random.random() > 0.5:
                manifest["dependencies"]["lib_auth_token"] = {"locked_version": "1.2.0"}

        with open(f"repo/build_settings/manifests/{commit}.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    # 3. Generate Fragmented Logs
    for pool in pools:
        num_workers = 40 if pool != target_pool else 45
        for w in range(num_workers):
            is_target_worker = (pool == target_pool and w == 23) # Hardcode the location of the fatal error
            
            log_content = generate_ansi_garbage_log(
                lines=random.randint(100, 200),
                is_fatal=is_target_worker,
                fatal_lib=target_lib,
                fatal_actual=actual_version
            )
            
            with open(f"ci_logs/node_pool_{pool}/worker_{w}_trace.log", "w", encoding="utf-8") as f:
                f.write(log_content)

if __name__ == "__main__":
    build_env()
