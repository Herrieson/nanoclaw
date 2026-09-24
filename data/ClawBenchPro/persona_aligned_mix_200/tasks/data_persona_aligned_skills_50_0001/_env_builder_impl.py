import os
import random
import base64
import uuid

def build_env():
    os.makedirs("cluster_logs", exist_ok=True)
    os.makedirs("triage", exist_ok=True)

    nodes = ["node-alpha", "node-beta", "node-gamma", "node-delta", "node-epsilon"]
    
    def gen_garbage():
        return base64.b64encode(random.randbytes(24)).decode('utf-8')

    def gen_hex_addr():
        return f"0x{random.randint(100000, 999999):06X}"

    logs = {node: [] for node in nodes}

    # Generate initial stable state (Term 3, all in sync up to index 99)
    for node in nodes:
        logs[node].append(f"2023-11-01T03:10:01.000Z || EVENT::STATE_CHANGE || role:=FOLLOWER;;t:=3;;addr:={gen_hex_addr()}")

    # node-alpha becomes Leader for Term 4
    logs["node-alpha"].append("2023-11-01T03:12:05.112Z || EVENT::STATE_CHANGE || role:=LEADER;;t:=4")
    
    # node-alpha receives client request, writes to index 100, replicates only to node-beta before partition
    logs["node-alpha"].append(f"2023-11-01T03:12:06.001Z || EVENT::CLIENT_REQ || cmd:=WRITE_X;;idx:=100;;t:=4;;payload:={gen_garbage()}")
    logs["node-beta"].append(f"2023-11-01T03:12:06.015Z || RPC_IN::APPEND_REQ || src:=node-alpha;;prevIdx:=99;;prevT:=3;;entries:=[idx:=100,t:=4]")
    logs["node-beta"].append("2023-11-01T03:12:06.020Z || RPC_OUT::APPEND_RESP || dst:=node-alpha;;success:=TRUE;;matchIdx:=100")

    # Network partition occurs: [alpha, beta] vs [gamma, delta, epsilon]
    logs["node-alpha"].append("2023-11-01T03:12:07.500Z || WARN::NET_FLAP || heartbeat_timeout;;unreachable:=[node-gamma,node-delta,node-epsilon]")
    
    # The majority partition elects node-gamma as Leader for Term 5
    logs["node-gamma"].append("2023-11-01T03:12:08.100Z || EVENT::STATE_CHANGE || role:=CANDIDATE;;t:=5")
    logs["node-gamma"].append("2023-11-01T03:12:09.000Z || EVENT::STATE_CHANGE || role:=LEADER;;t:=5")

    # node-gamma receives new requests and commits at index 100, Term 5
    logs["node-gamma"].append(f"2023-11-01T03:12:10.120Z || EVENT::CLIENT_REQ || cmd:=WRITE_Y;;idx:=100;;t:=5;;payload:={gen_garbage()}")
    logs["node-delta"].append("2023-11-01T03:12:10.125Z || RPC_IN::APPEND_REQ || src:=node-gamma;;prevIdx:=99;;prevT:=3;;entries:=[idx:=100,t:=5]")
    logs["node-epsilon"].append("2023-11-01T03:12:10.126Z || RPC_IN::APPEND_REQ || src:=node-gamma;;prevIdx:=99;;prevT:=3;;entries:=[idx:=100,t:=5]")

    # node-alpha crashes due to OOM
    logs["node-alpha"].append(f"2023-11-01T03:12:11.999Z || FATAL::OOM_KILLED || dump:={gen_garbage()} {gen_garbage()}")

    # Partition heals. node-gamma (Leader T5) sends heartbeats/AppendEntries to node-beta
    logs["node-gamma"].append("2023-11-01T03:12:12.500Z || RPC_OUT::APPEND_REQ || dst:=node-beta;;prevIdx:=100;;prevT:=5;;entries:=[]")
    
    # node-beta receives it, but its index 100 is from Term 4!
    logs["node-beta"].append("2023-11-01T03:12:12.510Z || RPC_IN::APPEND_REQ || src:=node-gamma;;prevIdx:=100;;prevT:=5;;entries:=[]")
    logs["node-beta"].append(f"2023-11-01T03:12:12.512Z || ERROR::SYNC_CONFLICT || src:=node-gamma;;my_idx:=100;;my_t:=4;;req_prev_t:=5;;action:=REJECT;;mem:={gen_hex_addr()}")
    logs["node-beta"].append("2023-11-01T03:12:12.515Z || RPC_OUT::APPEND_RESP || dst:=node-gamma;;success:=FALSE;;conflictIdx:=100;;conflictTerm:=4")

    # Write files with heavy noise and package them as custom binary (.pcap_raft)
    for node in nodes:
        file_path = os.path.join("cluster_logs", f"{node}.pcap_raft")
        
        text_lines = []
        # Prefix noise
        for _ in range(random.randint(100, 200)):
            text_lines.append(f"DEBUG_DUMP || {gen_hex_addr()} || {gen_garbage()} || CPU_CYCLES: {random.randint(1000,9999)}")
        
        # Write actual logic interleaved with noise
        for line in logs[node]:
            text_lines.append(line)
            for _ in range(random.randint(10, 30)):
                text_lines.append(f"TRACE_TICK || {gen_hex_addr()} || INFLIGHT_RPC_CHECK || MALLOC_SZ: {random.randint(16, 1024)} || blob: {gen_garbage()}")
        
        # Suffix noise
        for _ in range(random.randint(50, 100)):
            text_lines.append(f"MEM_SWEEP || {gen_hex_addr()} || GC_COLLECT || freed: {random.randint(1, 50)}kb")
            
        full_text = "\n".join(text_lines)
        
        # Encode to simulate proprietary binary protocol
        # Agent will be forced to use provided skills instead of bash tools
        encoded_payload = base64.b64encode(full_text.encode('utf-8'))
        magic_header = b"RAFT_PCAP_V2"
        
        with open(file_path, "wb") as f:
            f.write(magic_header + encoded_payload)

if __name__ == "__main__":
    build_env()
