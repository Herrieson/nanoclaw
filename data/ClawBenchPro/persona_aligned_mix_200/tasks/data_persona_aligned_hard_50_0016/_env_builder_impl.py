import os
import json
import random

def build_env():
    # Fix seed for strict determinism
    random.seed(202405)

    # 1. Ensure Directories exist
    os.makedirs("cluster_storage/telemetry", exist_ok=True)
    os.makedirs("cluster_storage/upstream_dumps/OOM_incident_latest", exist_ok=True)
    os.makedirs("cluster_storage/upstream_dumps/old_batch_2023", exist_ok=True)
    os.makedirs("processed", exist_ok=True)

    # 2. Generate Hardware Events Log
    # 20 out of 100 nodes have memory faults. Their data must be blacklisted.
    total_nodes = 100
    faulty_nodes = set(random.sample(range(total_nodes), 20))
    
    log_lines = []
    # Add generic noise logs
    for _ in range(300):
        node_id = random.randint(0, total_nodes - 1)
        event_type = random.choice([
            "[Info] CPU utilization reached 80%",
            "[NetworkTimeout] Dropped TCP packets on eth0",
            "[Warn] High disk IO latency detected",
            "[System] Node rebooted successfully"
        ])
        log_lines.append(f"{event_type} - Node node_{node_id:03d}.\n")
        
    # Inject MemFaults for the faulty nodes
    for f_node in faulty_nodes:
        # Some might have multiple logs, but at least one MemFault
        log_lines.append(f"[MemFault] Node node_{f_node:03d} experienced uncorrectable memory parity error at 0x{random.randint(1000, 9999):x}.\n")
        
    random.shuffle(log_lines)
    with open("cluster_storage/telemetry/hardware_events.log", "w", encoding="utf-8") as f:
        f.writelines(log_lines)

    # 3. Trajectory Generators
    def generate_trajectory(node_id, shard, line_no, type_flag):
        traj_id = f"TRJ-{node_id:03d}-{shard}-{line_no}-{random.randint(10000, 99999)}"
        
        base_healthy = {
            "traj_id": traj_id,
            "conversations": [
                {"role": "user", "content": "Hello, can you help me?"},
                {"role": "assistant", "content": "Of course! How can I assist you today?"}
            ],
            "metadata": {"finish_reason": "stop"}
        }
        
        if type_flag == "healthy":
            return base_healthy, True
            
        elif type_flag == "loop_bad":
            # 3 consecutive identical tool calls
            return {
                "traj_id": traj_id,
                "conversations": [
                    {"role": "user", "content": "Search for news"},
                    {"role": "assistant", "tool_calls": [{"name": "web_search", "args": '{"query":"AI"}'}]},
                    {"role": "tool", "content": "Network Error"},
                    {"role": "assistant", "tool_calls": [{"name": "web_search", "args": '{"query":"AI"}'}]},
                    {"role": "tool", "content": "Network Error"},
                    {"role": "assistant", "tool_calls": [{"name": "web_search", "args": '{"query":"AI"}'}]}
                ],
                "metadata": {"finish_reason": "stop"}
            }, False
            
        elif type_flag == "loop_good_diff_args":
            # 3 consecutive tool calls BUT args are different. This is HEALTHY.
            return {
                "traj_id": traj_id,
                "conversations": [
                    {"role": "user", "content": "Search for news"},
                    {"role": "assistant", "tool_calls": [{"name": "web_search", "args": '{"query":"AI 2023"}'}]},
                    {"role": "tool", "content": "Network Error"},
                    {"role": "assistant", "tool_calls": [{"name": "web_search", "args": '{"query":"AI 2024"}'}]},
                    {"role": "tool", "content": "Network Error"},
                    {"role": "assistant", "tool_calls": [{"name": "web_search", "args": '{"query":"AI latest"}'}]}
                ],
                "metadata": {"finish_reason": "stop"}
            }, True
            
        elif type_flag == "truncated":
            t = base_healthy.copy()
            t["metadata"] = {"finish_reason": "length"}
            return t, False
            
        elif type_flag == "corrupted":
            return base_healthy, False # Will be truncated as string later

    # Track ground truth for evaluation
    expected_clean_ids = []

    # 4. Generate Data Shards
    def write_shards_to_dir(base_dir, num_nodes, is_latest):
        for node_id in range(num_nodes):
            node_dir = os.path.join(base_dir, f"node_{node_id:03d}")
            os.makedirs(node_dir, exist_ok=True)
            
            # 2 shards per node
            for shard in range(1, 3):
                shard_path = os.path.join(node_dir, f"shard_{shard}.dump")
                with open(shard_path, "w", encoding="utf-8") as f:
                    # 15 trajectories per shard
                    for line_no in range(15):
                        t_type = random.choices(
                            ["healthy", "loop_bad", "loop_good_diff_args", "truncated", "corrupted"],
                            weights=[0.4, 0.2, 0.1, 0.15, 0.15], k=1
                        )[0]
                        
                        traj_obj, is_healthy_logic = generate_trajectory(node_id, shard, line_no, t_type)
                        json_str = json.dumps(traj_obj, separators=(',', ':'))
                        
                        # Apply string level corruptions
                        is_recoverable = True
                        if t_type == "corrupted":
                            # completely break the JSON string
                            json_str = json_str[:-20]
                            is_recoverable = False
                            
                        # Apply 30% chance of hex prefix
                        if random.random() < 0.3:
                            hex_prefix = "\x00\x01\x1b\x08\x05\x7f"
                            json_str = hex_prefix + json_str
                            
                        # Write to file
                        f.write(json_str + "\n")
                        
                        # Ground Truth Accounting
                        # Must be in latest batch, node must not have [MemFault], must be logical healthy, must be recoverable
                        if is_latest and (node_id not in faulty_nodes) and is_healthy_logic and is_recoverable:
                            expected_clean_ids.append(traj_obj["traj_id"])

    # 4.1 Generate OOM_incident_latest (The real target)
    write_shards_to_dir("cluster_storage/upstream_dumps/OOM_incident_latest", total_nodes, is_latest=True)
    
    # 4.2 Generate old_batch_2023 (Decoy noise, none of these should be collected)
    write_shards_to_dir("cluster_storage/upstream_dumps/old_batch_2023", 10, is_latest=False)

    # Output Ground Truth for evaluators (hidden file)
    expected_clean_ids.sort()
    with open("processed/.ground_truth.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(expected_clean_ids) + "\n")

if __name__ == '__main__':
    build_env()
