import os
import random
import base64
import uuid
import json

def build_env():
    # Create base directories
    os.makedirs("triage", exist_ok=True)
    os.makedirs("conf/routing", exist_ok=True)
    os.makedirs("logs/sys", exist_ok=True)
    os.makedirs("logs/rpc", exist_ok=True)

    clusters = ["cache-raft", "session-raft", "inventory-raft", "payment-raft"]
    
    # Generate topology configurations (Noise + Target)
    target_ip = "10.42.7.88"
    target_node = "node-payment-beta"
    
    for i in range(50):
        cluster_name = random.choice(clusters)
        status = random.choice(["active", "deprecated", "draining"])
        
        # Ensure only one active payment-raft config
        if cluster_name == "payment-raft" and status == "active":
            status = "deprecated"
            
        is_target_file = (i == 42)
        if is_target_file:
            cluster_name = "payment-raft"
            status = "active"

        nodes = []
        for j in range(5):
            if is_target_file and j == 2:
                nodes.append({"id": target_node, "ip": target_ip})
            else:
                nodes.append({
                    "id": f"node-{cluster_name[:4]}-{uuid.uuid4().hex[:4]}", 
                    "ip": f"10.{random.randint(10,50)}.{random.randint(1,255)}.{random.randint(1,255)}"
                })
        
        config_data = {
            "metadata": {
                "cluster": cluster_name,
                "version": f"v1.{random.randint(0, 20)}",
                "status": status,
                "last_updated": f"2023-11-01T0{random.randint(0,9)}:00:00Z"
            },
            "mesh_routes": nodes
        }
        
        with open(f"conf/routing/mesh_v{random.randint(100, 999)}_{i}.json", "w") as f:
            json.dump(config_data, f, indent=2)

    # Generate Syslogs with deep nesting
    target_trace_id = f"TXN-PAY-{uuid.uuid4().hex[:8].upper()}"
    
    for day in range(1, 3):
        for hour in range(0, 5):
            log_dir = f"logs/sys/2023/11/{day:02d}/{hour:02d}"
            os.makedirs(log_dir, exist_ok=True)
            
            for file_idx in range(10):
                file_path = os.path.join(log_dir, f"sys_event_{file_idx}.log")
                with open(file_path, "w") as f:
                    # Write noise logs
                    for _ in range(random.randint(50, 150)):
                        rand_cluster = random.choice(clusters)
                        rand_ip = f"10.{random.randint(10,50)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        if random.random() < 0.05:
                            # Decoy SYNC_CONFLICT for OTHER clusters
                            decoy_trace = f"TXN-DECOY-{uuid.uuid4().hex[:6]}"
                            f.write(f"2023-11-{day:02d}T{hour:02d}:{random.randint(10,59)}:00Z [{rand_cluster}] [ERROR] SYNC_CONFLICT detected! action=REJECT_APPEND, pod_ip={rand_ip}, trace_id={decoy_trace}\n")
                        else:
                            f.write(f"2023-11-{day:02d}T{hour:02d}:{random.randint(10,59)}:00Z [{rand_cluster}] [INFO] Heartbeat OK. pod_ip={rand_ip}, latency={random.randint(1, 100)}ms\n")
                    
                    # Inject Target Log
                    if day == 1 and hour == 3 and file_idx == 7:
                        f.write(f"2023-11-01T03:12:12.512Z [payment-raft] [FATAL] SYNC_CONFLICT! Brain-split partition recovery failed. action=REJECT_APPEND_ENTRIES, pod_ip={target_ip}, trace_id={target_trace_id}\n")

    # Generate RPC Dumps
    # Target payload
    target_payload_dict = {"conflict_term": 4, "conflict_index": 100}
    target_b64 = base64.b64encode(json.dumps(target_payload_dict).encode('utf-8')).decode('utf-8')
    
    for i in range(500):
        is_target = (i == 256)
        trace_id = target_trace_id if is_target else f"TXN-{random.choice(['DECOY', 'PAY', 'CACHE'])}-{uuid.uuid4().hex[:8].upper()}"
        
        if not is_target:
            fake_payload = {"conflict_term": random.randint(1, 3), "conflict_index": random.randint(10, 99)}
            payload_b64 = base64.b64encode(json.dumps(fake_payload).encode('utf-8')).decode('utf-8')
        else:
            payload_b64 = target_b64

        dump_path = os.path.join("logs/rpc", f"dump_{trace_id}.dat")
        with open(dump_path, "w") as f:
            f.write("========== RPC HEX DUMP START ==========\n")
            f.write(f"TIMESTAMP: 1698808{random.randint(100, 999)}\n")
            f.write(f"TRACE_ID: {trace_id}\n")
            f.write(f"PROTOCOL: RAFT_V2_CUSTOM\n")
            f.write("HEADER_CHECKSUM: 0x" + "".join(random.choices("0123456789ABCDEF", k=8)) + "\n")
            f.write("-" * 40 + "\n")
            f.write(f"PAYLOAD_B64: {payload_b64}\n")
            f.write("-" * 40 + "\n")
            f.write("========== RPC HEX DUMP END ==========\n")

if __name__ == "__main__":
    build_env()
