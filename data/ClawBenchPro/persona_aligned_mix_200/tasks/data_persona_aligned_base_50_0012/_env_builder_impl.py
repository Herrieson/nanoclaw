import os
import json
import random
import string

def generate_garbage_log(lines=800):
    log = []
    # Generate noisy parallel build output with ANSI codes and hex dumps
    for i in range(lines):
        timestamp = f"[2023-10-27T03:14:{random.randint(10,59)}.{random.randint(100,999)}Z]"
        ansi_color = random.choice(['\x1b[32m', '\x1b[33m', '\x1b[36m', '\x1b[90m', '\x1b[0m'])
        
        chance = random.random()
        if chance > 0.95:
            # Simulate memory map / hex dump garbage from a crash or verbose debug
            garbage = "".join(random.choices(string.hexdigits, k=48))
            log.append(f"{timestamp} {ansi_color}[DEBUG] block dump: 0x{garbage}\x1b[0m")
        elif chance > 0.85:
            # Simulate compiler warnings
            log.append(f"{timestamp} \x1b[33mwarning:\x1b[0m unused variable 'ctx_{i}' [-Wunused-variable]")
        else:
            # Normal build progress
            log.append(f"{timestamp} {ansi_color}[{random.randint(1,100)}%] Building CXX object src/CMakeFiles/core.dir/module_{i}.cpp.o\x1b[0m")

    # Insert the actual conflict hidden deep inside the noise
    conflict_idx = int(lines * 0.65)
    timestamp = "[2023-10-27T03:14:45.123Z]"
    error_msg = (
        f"{timestamp} \x1b[31mFAILED:\x1b[0m src/CMakeFiles/core.dir/network.cpp.o\n"
        f"{timestamp} /usr/bin/clang++ -O3 -DNDEBUG -std=gnu++20 -MD -MT src/CMakeFiles/core.dir/network.cpp.o -MF src/CMakeFiles/core.dir/network.cpp.o.d -o src/CMakeFiles/core.dir/network.cpp.o -c /usr/src/app/src/network.cpp\n"
        f"{timestamp} \x1b[1m/usr/src/app/vendor/fmt/include/fmt/core.h:12:2:\x1b[0m "
        f"\x1b[31mfatal error:\x1b[0m static assertion failed: \"\x1b[35mfmtlib\x1b[0m version mismatch: "
        f"expected \x1b[32m9.1.0\x1b[0m, but pulled in \x1b[31m8.0.1\x1b[0m via legacy module\"\n"
        f"{timestamp}  12 | #error \"fmtlib version mismatch\"\n"
        f"{timestamp}     |  ^~~~~\n"
        f"{timestamp} 1 error generated.\n"
        f"{timestamp} ninja: build stopped: subcommand failed."
    )
    log.insert(conflict_idx, error_msg)

    # Insert a distractor warning that is not the fatal error
    warn_idx = int(lines * 0.25)
    warn_msg = (
        f"[2023-10-27T03:14:22.000Z] \x1b[33mWARNING:\x1b[0m boost version 1.82.0 shadows global installation of 1.74.0, "
        f"compilation will proceed using the local vendor copy."
    )
    log.insert(warn_idx, warn_msg)

    return "\n".join(log)

def build_env():
    # Directories
    os.makedirs("ci_logs", exist_ok=True)
    os.makedirs("repo/build_settings", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    # Write messy log file
    with open("ci_logs/pipeline_stage_3.log", "w", encoding="utf-8") as f:
        f.write(generate_garbage_log())

    # Write nested manifest configuration
    deps = {
        "project_metadata": {
            "name": "core_engine",
            "team": "backend",
            "ci_tags": ["docker", "cxx20", "avx512", "ubuntu-22.04"]
        },
        "environments": {
            "production": {
                "compiler": "clang-14",
                "dependencies": {
                    "third_party": [
                        {"package": "boost", "version": "1.82.0", "link": "static"},
                        {"package": "fmtlib", "version": "9.1.0", "link": "shared"},
                        {"package": "gtest", "version": "1.14.0", "link": "static", "scope": "test"},
                        {"package": "openssl", "version": "3.0.8", "link": "shared"}
                    ],
                    "internal": [
                        {"package": "libcore_network", "version": "2.4.1"}
                    ]
                }
            }
        }
    }

    with open("repo/build_settings/dependencies.json", "w", encoding="utf-8") as f:
        json.dump(deps, f, indent=4)

if __name__ == "__main__":
    build_env()
