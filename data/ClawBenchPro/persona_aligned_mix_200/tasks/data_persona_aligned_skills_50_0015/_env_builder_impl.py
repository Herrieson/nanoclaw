import os
import random
import json
import struct

def build_env():
    # Fix the seed for deterministic sandbox creation
    random.seed(73)
    
    os.makedirs("mpc_traces", exist_ok=True)
    os.makedirs("optimizations", exist_ok=True)

    gates_metadata = []
    telemetry_db = {}

    # Generate normal background noise gates (small communication overhead)
    for i in range(150):
        gid = f"GATE_{i:04X}"
        pkt_ref = f"PKT_{random.randint(100000, 999999)}"
        payload_size = random.randint(10, 100)
        
        gates_metadata.append({"gate_id": gid, "packet_ref": pkt_ref})
        telemetry_db[pkt_ref] = payload_size

    # Inject the 3 massive bottleneck gates (anomalously large communication payload)
    bottleneck_gates = [
        ("GATE_F9A1", 3500),
        ("GATE_F9A2", 2800),
        ("GATE_F9A3", 2100)
    ]
    
    for gid, size in bottleneck_gates:
        pkt_ref = f"PKT_{random.randint(100000, 999999)}"
        gates_metadata.append({"gate_id": gid, "packet_ref": pkt_ref})
        telemetry_db[pkt_ref] = size

    # Shuffle to distribute the bottlenecks randomly
    random.shuffle(gates_metadata)

    # Write the hidden ground truth databases for skills to query
    # Agent is not supposed to know or read these directly (and shouldn't be able to guess the names easily)
    with open("mpc_traces/.meta_decode_db.json", "w", encoding="utf-8") as f:
        json.dump(gates_metadata, f)
        
    with open("mpc_traces/.telemetry_db.json", "w", encoding="utf-8") as f:
        json.dump(telemetry_db, f)

    # Generate the dummy binary dump file to act as an obstacle
    with open("mpc_traces/node_eval.mpc_dump", "wb") as f:
        # Fake magic headers
        f.write(b"MPC_CORE_DUMP_V2\x00\x00\x01\x0A")
        # Fake binary body (just random noise to prevent text-based reading)
        for _ in range(500):
            f.write(struct.pack("I", random.randint(0, 0xFFFFFFFF)))

if __name__ == "__main__":
    build_env()
