import os
import argparse
import json
import csv

def generate_noise_logs(lines=500, lang="cpp"):
    noise = []
    if lang == "cpp":
        for i in range(lines):
            noise.append(f"[INFO] Compiling object file {i}.o ... OK")
            if i % 50 == 0:
                noise.append(f"[WARN] Variable 'tmp_{i}' is unused.")
    else:
        for i in range(lines):
            noise.append(f"Collecting package_foo_{i}...")
            noise.append(f"Downloading package_foo_{i}-1.0.tar.gz (10kB)")
    return noise

def build_turn_1():
    os.makedirs("source/trade_core", exist_ok=True)
    os.makedirs("source/risk_engine", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("ci_reports", exist_ok=True)

    # 1. Base Image Specs
    specs = {
        "Boost": ["1.74.0", "1.75.0", "1.76.0", "1.80.0"],
        "OpenSSL": ["1.1.1", "3.0.0", "3.0.5", "3.0.8"],
        "pandas": ["1.3.5", "1.4.0", "1.5.0", "1.5.3", "1.5.4"],
        "pydantic": ["1.10.0", "1.10.8", "2.1.0", "2.2.0"]
    }
    with open("config/base_image_specs.json", "w", encoding="utf-8") as f:
        json.dump(specs, f, indent=4)

    # 2. Source Files
    with open("source/trade_core/conanfile.txt", "w", encoding="utf-8") as f:
        f.write("[requires]\nBoost/1.74.0\nOpenSSL/1.1.1\n")
    
    with open("source/risk_engine/requirements.txt", "w", encoding="utf-8") as f:
        f.write("pandas==1.3.5\npydantic==2.1.0\n")

    # 3. Logs with hidden exact constraints
    cpp_logs = generate_noise_logs(200, "cpp")
    cpp_error = [
        "[ERROR] CMake Error at CMakeLists.txt:42:",
        "  Fatal: Base Image v2.0 strictly requires ALPN support not present in OpenSSL 1.1.1.",
        "  Additionally, C++20 ABI compatibility failed with Boost 1.74.0.",
        "  RESOLUTION_REQUIRED: Boost >= 1.75.0 AND OpenSSL >= 3.0.0 to build.",
        "  Aborting."
    ]
    cpp_logs = cpp_logs[:120] + cpp_error + cpp_logs[120:]
    with open("logs/trade_core_build.log", "w", encoding="utf-8") as f:
        f.write("\n".join(cpp_logs))

    py_logs = generate_noise_logs(150, "python")
    py_error = [
        "ERROR: Cannot install -r requirements.txt (line 1) and pydantic==2.1.0 (line 2) because these package versions have conflicting dependencies.",
        "The conflict is caused by:",
        "    The user requested pandas==1.3.5",
        "    Base image OS core lib requires pandas>=1.5.0 for C-extension compatibility.",
        "    The user requested pydantic==2.1.0",
        "    pydantic 2.x rust bindings are missing in this container, constraint: pydantic < 2.0.0 is enforced.",
        "ResolutionImpossible: Check your constraints."
    ]
    py_logs = py_logs[:80] + py_error + py_logs[80:]
    with open("logs/risk_engine_build.log", "w", encoding="utf-8") as f:
        f.write("\n".join(py_logs))

def build_turn_2():
    os.makedirs("source/quant_service", exist_ok=True)
    # Option A: violates Boost rule
    # Option B: violates pandas rule
    # Option C: completely valid based on turn 1 rules
    quant_deps = {
        "Option_A": {"Boost": "1.74.0", "OpenSSL": "3.0.5", "pandas": "1.5.3", "pydantic": "1.10.8"},
        "Option_B": {"Boost": "1.76.0", "OpenSSL": "3.0.5", "pandas": "1.4.0", "pydantic": "1.10.8"},
        "Option_C": {"Boost": "1.80.0", "OpenSSL": "3.0.5", "pandas": "1.5.3", "pydantic": "1.10.8"}
    }
    with open("source/quant_service/deps.json", "w", encoding="utf-8") as f:
        json.dump(quant_deps, f, indent=4)

def build_turn_3():
    os.makedirs("security", exist_ok=True)
    
    # CVE impacts OpenSSL 3.0.5 (used in Option C and possibly turn 1 proposal)
    # and pandas 1.5.3. Safe versions are 3.0.8 and 1.5.4 respectively.
    csv_data = [
        ["CVE_ID", "Library", "Vulnerable_Versions", "Safe_Version_Recommendation", "Severity"],
        ["CVE-2023-1122", "OpenSSL", "<= 3.0.5", "3.0.8", "CRITICAL"],
        ["CVE-2023-9988", "pandas", "1.5.0 - 1.5.3", "1.5.4", "HIGH"],
        ["CVE-2023-0001", "Boost", "1.70.0", "1.75.0", "LOW"]
    ]
    with open("security/cve_blacklist.csv", "w", encoding="utf-8", newline='') as f:
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
