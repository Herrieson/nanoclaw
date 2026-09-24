import os
import json
import uuid

def generate_corrupted_api_logs():
    os.makedirs("sandbox_traces", exist_ok=True)
    
    # Generate a dummy binary file to prevent text parsing
    # simulating corrupted or proprietary raw cache
    cache_file = "sandbox_traces/edr_agent_cache.db"
    with open(cache_file, "wb") as f:
        # Write magic headers and random bytes
        f.write(b"EDR_CACHE_V2\x00\xFF\xAA\xBB")
        f.write(os.urandom(1024 * 512)) # 512KB of unreadable binary junk

def generate_proprietary_memory_dump():
    os.makedirs("mem_dumps", exist_ok=True)
    dump_file = "mem_dumps/region_0x0400000.hvdmp"
    
    # Generate a proprietary hypervisor memory dump binary
    with open(dump_file, "wb") as f:
        f.write(b"HVDMP_v3.0\x00\x00\x00\x00\x01\x02\x03\x04")
        f.write(os.urandom(1024 * 1024)) # 1MB of binary noise

def generate_noise_files():
    os.makedirs("intel", exist_ok=True)
    
    # Useless complex JSON config
    config_data = {
        "sandbox_version": "3.1-rc2",
        "analyzer": {
            "modules": {
                "hooking": {"enabled": True, "timeout": 600},
                "network": {"capture_pcap": True, "interface": "eth0"}
            },
            "heuristics": [
                {"id": "H001", "weight": 0.5},
                {"id": "H002", "weight": 0.8}
            ]
        },
        "target_info": {
            "md5": uuid.uuid4().hex,
            "sha256": uuid.uuid4().hex * 2,
            "submission_id": "SUB-8892"
        }
    }
    with open("sandbox_traces/cuckoo_sys_conf.json", "w") as f:
        json.dump(config_data, f, indent=4)

def build_env():
    generate_corrupted_api_logs()
    generate_proprietary_memory_dump()
    generate_noise_files()

if __name__ == "__main__":
    build_env()
