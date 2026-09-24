import os
import random

def chunk_string(s, length):
    return '\n'.join(s[i:i+length] for i in range(0, len(s), length))

def generate_hex(bytes_len):
    return ''.join(random.choices("0123456789abcdef", k=bytes_len * 2))

def build_env():
    # Fix the seed for deterministic sandbox creation
    random.seed(73)
    
    os.makedirs("mpc_traces", exist_ok=True)
    os.makedirs("optimizations", exist_ok=True)

    with open("mpc_traces/node_eval.diag", "w", encoding="utf-8") as f:
        f.write("=== MPC CORE ENGINE v2.1.4 DIAGNOSTIC LOG ===\n")
        f.write("RUNTIME_CONFIG: { 'parties': 3, 'protocol': 'YaoGC_half_gates', 'curve': 'secp256k1' }\n")
        f.write("INIT: OT Extension Phase Completed.\n\n")

        gates = []
        # Generate normal background noise gates (small communication overhead)
        for i in range(150):
            gid = f"GATE_{i:04X}"
            gtype = random.choice(["XOR", "AND", "INV", "XNOR"])
            payload = generate_hex(random.randint(10, 100))
            gates.append((gid, gtype, payload))

        # Inject the 3 massive bottleneck gates (anomalously large communication payload)
        gates.append(("GATE_F9A1", "AND", generate_hex(3500)))
        gates.append(("GATE_F9A2", "AND", generate_hex(2800)))
        gates.append(("GATE_F9A3", "AND", generate_hex(2100)))

        # Shuffle to distribute the bottlenecks randomly in the diagnostic file
        random.shuffle(gates)

        for gid, gtype, payload in gates:
            f.write(f"--- [OP_TRACE] {gid} [{gtype}] ---\n")
            
            # Random noise lines
            if random.random() < 0.3:
                f.write(f"state_check: OK (wire_entropy={random.uniform(0.9, 1.0):.4f})\n")
            if random.random() < 0.15:
                f.write(f"warn: minor sync delay at {gid}, auto-recovered.\n")
                
            f.write("== WIRE_EXCHANGE_BUFFER ==\n")
            f.write(chunk_string(payload, 64) + "\n")
            f.write("== END_BUFFER ==\n\n")

if __name__ == "__main__":
    build_env()
