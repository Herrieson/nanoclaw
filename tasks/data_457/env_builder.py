import os
import gzip
import random

def build_env():
    base_dir = "assets/data_457"
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Deterministic generation
    random.seed(457)

    ips = [
        "192.168.1.10", "10.0.0.25", "172.16.4.8", 
        "203.0.113.5", "198.51.100.14"
    ]
    
    # Pre-calculated expected crashes to generate
    # We will track exactly how many we put in
    expected_counts = {
        "192.168.1.10": 4,
        "10.0.0.25": 1,
        "172.16.4.8": 3,
        "203.0.113.5": 0,
        "198.51.100.14": 2
    }
    
    # Distribute the events into files
    file_configs = [
        {"name": "server_A/app.log", "is_gz": False, "crashes": ["192.168.1.10", "172.16.4.8"]},
        {"name": "server_A/app.log.1.gz", "is_gz": True, "crashes": ["198.51.100.14", "192.168.1.10"]},
        {"name": "server_B/worker.log", "is_gz": False, "crashes": ["10.0.0.25", "172.16.4.8"]},
        {"name": "server_B/archive/worker.log.old.gz", "is_gz": True, "crashes": ["192.168.1.10", "172.16.4.8"]},
        {"name": "server_C/misc.log", "is_gz": False, "crashes": ["198.51.100.14", "192.168.1.10"]},
        {"name": "server_C/misc.log.gz", "is_gz": True, "crashes": []} # Noise
    ]
    
    timestamp = 1697000000
    
    for config in file_configs:
        file_path = os.path.join(logs_dir, config["name"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        lines = []
        crashes_to_inject = config["crashes"].copy()
        random.shuffle(crashes_to_inject)
        
        # Generate 100 random log lines per file
        for _ in range(100):
            timestamp += random.randint(1, 60)
            if crashes_to_inject and random.random() < 0.1:
                # Inject crash
                crash_ip = crashes_to_inject.pop()
                lines.append(f"[{timestamp}] INFO Request from {crash_ip}\n")
                lines.append(f"[{timestamp+1}] DEBUG Processing data block\n")
                lines.append(f"[{timestamp+2}] ERROR Segmentation fault (core dumped)\n")
            else:
                # Normal request
                normal_ip = random.choice(ips)
                lines.append(f"[{timestamp}] INFO Request from {normal_ip}\n")
                lines.append(f"[{timestamp+1}] DEBUG Processing data block\n")
                lines.append(f"[{timestamp+2}] INFO Request completed successfully\n")
        
        # If any crashes left, put them at the end
        for crash_ip in crashes_to_inject:
            timestamp += random.randint(1, 60)
            lines.append(f"[{timestamp}] INFO Request from {crash_ip}\n")
            lines.append(f"[{timestamp+1}] DEBUG Processing data block\n")
            lines.append(f"[{timestamp+2}] ERROR Segmentation fault (core dumped)\n")
            
        content = "".join(lines).encode('utf-8')
        if config["is_gz"]:
            with gzip.open(file_path, 'wb') as f:
                f.write(content)
        else:
            with open(file_path, 'wb') as f:
                f.write(content)

if __name__ == "__main__":
    build_env()
