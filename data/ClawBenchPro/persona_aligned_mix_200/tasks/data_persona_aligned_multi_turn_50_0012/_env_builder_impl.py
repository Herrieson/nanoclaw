import os
import argparse
import json

def generate_ansi_log(content):
    # 用一些 ANSI 转义字符污染文本，模拟 Docker 终端乱码
    ansi_red = "\x1b[31;1m"
    ansi_green = "\x1b[32m"
    ansi_reset = "\x1b[0m"
    ansi_bold = "\x1b[1m"
    
    polluted_lines = []
    for line in content.split('\n'):
        if "ERROR" in line or "Conflict" in line:
            polluted_lines.append(f"{ansi_red}{line}{ansi_reset}")
        elif "WARN" in line:
            polluted_lines.append(f"\x1b[33m{line}{ansi_reset}")
        elif "INFO" in line:
            polluted_lines.append(f"{ansi_green}{line}{ansi_reset}")
        else:
            polluted_lines.append(f"{ansi_bold}{line}{ansi_reset}")
    return '\n'.join(polluted_lines)

def build_turn_1():
    os.makedirs("pipeline_logs", exist_ok=True)
    os.makedirs("src", exist_ok=True)
    os.makedirs("team_inventory", exist_ok=True)

    # 1. 制造带乱码的日志 (包含依赖冲突)
    log_content = """[INFO] Running Conan install...
[INFO] conan install . -s build_type=Release -s compiler=gcc -s compiler.version=11
[WARN] Poco/1.9.4: requirement Boost/1.69.0 overridden by your conanfile
[ERROR] ConanException: Conflict in Boost/1.74.0:
[ERROR]     'Poco/1.9.4' requires 'Boost/1.69.0' while 'project' requires 'Boost/1.74.0'.
[ERROR]     To fix this conflict you need to override the package 'Boost' in your root package.
[ERROR] CMake Error at CMakeLists.txt:24 (find_package):
[ERROR]   Could not find a configuration file for package "fmt" that is compatible
[ERROR]   with requested version "8.1.1".
[INFO] Build step failed with exit code 1."""
    
    with open("pipeline_logs/build_job_1042.log", "w", encoding="utf-8") as f:
        f.write(generate_ansi_log(log_content))

    # 2. 模拟 conanfile.py
    conanfile_content = """from conans import ConanFile

class MyProjectConan(ConanFile):
    name = "MyProject"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    requires = (
        "Boost/1.74.0",
        "Poco/1.9.4",
        "fmt/8.1.1"
    )
    generators = "cmake"
"""
    with open("src/conanfile.py", "w", encoding="utf-8") as f:
        f.write(conanfile_content)

    # 3. 官方安全基线
    inventory = {
        "libraries": {
            "Boost": {
                "min_version": "1.74.0",
                "status": "APPROVED",
                "notes": "Core utility. Do not downgrade."
            },
            "Poco": {
                "min_version": "1.10.1",
                "status": "APPROVED",
                "notes": "Upgraded due to CVE in 1.9.x. Requires C++11 ABI."
            },
            "fmt": {
                "min_version": "8.1.1",
                "status": "APPROVED"
            }
        }
    }
    with open("team_inventory/approved_libs.json", "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4)


def build_turn_2():
    os.makedirs("pipeline_logs", exist_ok=True)
    os.makedirs("mr_changes", exist_ok=True)

    # 1. 开发者的 Patch diff (表面修了版本，但埋了 ABI 的坑)
    diff_content = """--- src/conanfile.py
+++ src/conanfile.py
@@ -6,8 +6,9 @@
     settings = "os", "compiler", "build_type", "arch"
+    default_options = {"*:shared": True, "Poco:compiler.libcxx": "libstdc++"}
     requires = (
         "Boost/1.74.0",
-        "Poco/1.9.4",
+        "Poco/1.10.1",
         "fmt/8.1.1"
     )
     generators = "cmake"
"""
    with open("mr_changes/patch_01.diff", "w", encoding="utf-8") as f:
        f.write(diff_content)

    # 2. 新的链接期报错日志 (ABI 冲突)
    # Poco被强制用老ABI(libstdc++)编译，而主工程用gcc 11默认的新ABI(libstdc++11)
    log_content2 = """[INFO] Running CMake build...
[INFO] Linking CXX executable app
[ERROR] /usr/bin/ld: CMakeFiles/app.dir/main.cpp.o: in function `main':
[ERROR] main.cpp:(.text+0x54): undefined reference to `Poco::Net::HTTPClientSession::HTTPClientSession(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, unsigned short)'
[ERROR] collect2: error: ld returned 1 exit status
[ERROR] ninja: build stopped: subcommand failed.
[INFO] Build step failed with exit code 1."""
    
    with open("pipeline_logs/build_job_1043.log", "w", encoding="utf-8") as f:
        f.write(generate_ansi_log(log_content2))


def build_turn_3():
    os.makedirs("pipeline_logs", exist_ok=True)
    os.makedirs("prod_deploy", exist_ok=True)

    # 1. 运行时崩溃日志
    # 因为是用 GCC 11 / C++11 ABI 编译的，需要较新的 libstdc++.so.6
    log_content3 = """[INFO] Starting Docker container...
[FATAL] /opt/app/bin/my_app: /usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.29' not found (required by /opt/app/bin/my_app)
[FATAL] /opt/app/bin/my_app: /usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `CXXABI_1.3.13' not found (required by /opt/app/bin/my_app)
[INFO] Container exited with code 127"""
    
    with open("pipeline_logs/runtime_crash_1044.log", "w", encoding="utf-8") as f:
        f.write(generate_ansi_log(log_content3))

    # 2. 坑人的基础镜像配置 (Ubuntu 18.04 只有 gcc 7)
    dockerfile_content = """FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY ./build/bin/my_app /opt/app/bin/

CMD ["/opt/app/bin/my_app"]
"""
    with open("prod_deploy/base_image.Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile_content)


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
