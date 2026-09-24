import os
import json
import random
import string
from datetime import datetime, timedelta

def generate_hex_tag():
    return "0x" + "".join(random.choices("0123456789ABCDEF", k=4))

def build_env():
    random.seed(42)  # Ensure deterministic generation for validation

    # Build directory trees
    for d in ["billing", "policies", "metrics", "actions"]:
        os.makedirs(d, exist_ok=True)

    target_departments = ["AI-Research", "Data-Analytics"]
    decoy_departments = ["Core-Prod", "Marketing-SEO", "Security-Ops"]

    # 1. Generate 500 Decoy Policies and 1 PROD_ACTIVE policy
    active_folder = f"policies/archive_{random.randint(10, 99)}"
    os.makedirs(active_folder, exist_ok=True)
    
    # Truth Mapping
    truth_mapping = {dept: [generate_hex_tag(), generate_hex_tag()] for dept in target_departments + decoy_departments}
    
    valid_tags = truth_mapping["AI-Research"] + truth_mapping["Data-Analytics"]
    
    for i in range(500):
        folder = f"policies/archive_{random.randint(10, 99)}"
        os.makedirs(folder, exist_ok=True)
        
        is_active = (i == 250)
        status = "PROD_ACTIVE" if is_active else random.choice(["DEPRECATED", "DRAFT", "TESTING", "ARCHIVED_V1"])
        
        policy_doc = {
            "_meta": {
                "status": status,
                "author": "J.Doe" if is_active else random.choice(["System", "Intern", "J.Doe"]),
                "timestamp": datetime.now().isoformat()
            },
            "enterprise_cloud_governance": {
                "global_region": {
                    "tag_mappings": {
                        "departments": {}
                    }
                }
            }
        }
        
        if is_active:
            # Inject Truth
            for dept, tags in truth_mapping.items():
                policy_doc["enterprise_cloud_governance"]["global_region"]["tag_mappings"]["departments"][dept] = {
                    "cost_centers": [{"id": f"CC-{random.randint(100,999)}", "obfuscated_tag": t} for t in tags]
                }
            file_path = os.path.join(active_folder, f"policy_v3_final_{i}.json")
        else:
            # Inject Garbage
            for dept in target_departments + decoy_departments:
                policy_doc["enterprise_cloud_governance"]["global_region"]["tag_mappings"]["departments"][dept] = {
                    "cost_centers": [{"id": f"CC-{random.randint(100,999)}", "obfuscated_tag": generate_hex_tag()} for _ in range(2)]
                }
            file_path = os.path.join(folder, f"policy_draft_{i}.json")
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(policy_doc, f, indent=4)

    # Trackers for Truth
    expected_to_delete = []

    # 2. Generate Billing Data
    regions = ["aws/us-east-1", "aws/us-west-2", "gcp/us-central1", "gcp/europe-west1"]
    for r in regions:
        os.makedirs(f"billing/{r}", exist_ok=True)
    
    resources = [] # (res_id, type, state, tag_hex, avg_util_target)
    
    # Generate Resources
    for i in range(2000):
        res_id = f"res-{uuid_like()}"
        res_type = random.choice(["Block-Disk", "Compute-GPU", "Compute-CPU", "Snapshot", "Network-LB"])
        dept = random.choice(target_departments + decoy_departments)
        tag_hex = random.choice(truth_mapping[dept])
        
        if res_type == "Block-Disk":
            state = random.choice(["Available", "Detached", "InUse", "Failed", "Creating"])
            if dept in target_departments and state in ["Available", "Detached"]:
                expected_to_delete.append(res_id)
            resources.append((res_id, res_type, state, tag_hex, None))
            
        elif res_type == "Compute-GPU":
            state = random.choice(["Running", "Stopped"])
            if state == "Running":
                # Decide if it's idle (<10%) or active (>10%)
                is_idle = random.choice([True, False])
                if is_idle:
                    avg_util_target = random.randint(0, 8)
                    if dept in target_departments:
                        expected_to_delete.append(res_id)
                else:
                    avg_util_target = random.randint(15, 99)
            else:
                avg_util_target = 0 # Stopped
                if dept in target_departments:
                    expected_to_delete.append(res_id)
                    
            resources.append((res_id, res_type, state, tag_hex, avg_util_target))
            
        else:
            state = random.choice(["Running", "Available", "InUse"])
            resources.append((res_id, res_type, state, tag_hex, None))

    # Write Billing Files
    chunk_size = 500
    for chunk_idx in range(0, len(resources), chunk_size):
        chunk = resources[chunk_idx:chunk_idx+chunk_size]
        r = random.choice(regions)
        file_path = f"billing/{r}/export_part_{chunk_idx}.dat"
        
        lines = ["TX_ID|~|RES_ID|~|TYPE|~|STATE|~|COST|~|TAG_HEX"]
        for res in chunk:
            tx_id = f"tx-{uuid_like()[:8]}"
            cost = f"{random.uniform(10, 5000):.2f}"
            lines.append(f"{tx_id}|~|{res[0]}|~|{res[1]}|~|{res[2]}|~|{cost}|~|{res[3]}")
            
            # Inject noise
            if random.random() < 0.05:
                lines.append(random.choice([
                    "NULL_CORRUPT_LINE_0x000000",
                    "ERROR: connection timeout on row",
                    "\n",
                    f"tx-err|~|{res[0]}|~|UNKNOWN|~|UNKNOWN"
                ]))
                
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # 3. Generate Metric Logs
    log_lines = []
    base_time = datetime(2023, 10, 1, 0, 0, 0)
    
    for res in resources:
        if res[1] == "Compute-GPU":
            res_id = res[0]
            avg_util_target = res[4]
            # Generate 24 hourly logs for each GPU
            for hour in range(24):
                time_str = (base_time + timedelta(hours=hour)).isoformat() + "Z"
                
                # fluctuate utilization slightly around target
                if avg_util_target == 0:
                    util = 0
                else:
                    util = max(0, min(100, avg_util_target + random.randint(-3, 3)))
                    
                mem = max(0, min(100, util + random.randint(-10, 10)))
                log_lines.append(f"[{time_str}] gpu_metrics [INFO] res={res_id} util={util}% mem={mem}%")

    # Add massive noise logs
    for i in range(5000):
        time_str = (base_time + timedelta(minutes=random.randint(0, 1440))).isoformat() + "Z"
        noise = random.choice([
            f"[{time_str}] kernel: [ {random.uniform(1000, 9000):.4f}] usb 1-1: USB disconnect, device number {random.randint(1,10)}",
            f"[{time_str}] systemd[1]: Started Network Manager.",
            f"[{time_str}] nginx: [error] 404 Not Found",
            f"[{time_str}] sshd[{random.randint(100, 9999)}]: Invalid user admin from {random.randint(1,255)}.{random.randint(1,255)}.1.1"
        ])
        log_lines.append(noise)
        
    random.shuffle(log_lines)
    
    # Split logs into multiple nodes
    os.makedirs("metrics/nodes", exist_ok=True)
    logs_per_file = len(log_lines) // 10
    for i in range(10):
        with open(f"metrics/nodes/syslog_node_{i}.log", "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines[i*logs_per_file : (i+1)*logs_per_file]))

    # Secret Ground Truth (For Evaluation, invisible in standard Agent constraints but exists)
    with open(".ground_truth.json", "w") as f:
        json.dump(expected_to_delete, f)

def uuid_like():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))

if __name__ == "__main__":
    build_env()
