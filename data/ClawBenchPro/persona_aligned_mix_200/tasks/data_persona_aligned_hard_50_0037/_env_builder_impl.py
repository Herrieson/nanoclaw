import os
import struct
import random
import math
import json

def make_packet(is_valid, ts):
    sync = b'\x1a\xcf\xfc\x1d'
    ts_bytes = struct.pack('>I', ts)
    
    if is_valid:
        # Generate valid normalized quaternion [-1.0, 1.0]
        u1, u2, u3 = random.random(), random.random(), random.random()
        q1 = math.sqrt(1 - u1) * math.sin(2 * math.pi * u2)
        q2 = math.sqrt(1 - u1) * math.cos(2 * math.pi * u2)
        q3 = math.sqrt(u1) * math.sin(2 * math.pi * u3)
        q4 = math.sqrt(u1) * math.cos(2 * math.pi * u3)
    else:
        # Generate corrupted quaternions
        choice = random.choice([1, 2, 3])
        if choice == 1:
            q1, q2, q3, q4 = 5.4, -2.1, 0.0, 0.9  # Out of bounds
        elif choice == 2:
            q1 = float('nan')
            q2, q3, q4 = 0.5, 0.5, 0.5            # Contains NaN
        else:
            q1, q2, q3, q4 = float('inf'), 0.0, -1.5, 0.0 # Inf and out of bounds
            
    q_bytes = struct.pack('>ffff', q1, q2, q3, q4)
    crc = bytes([random.randint(0, 255), random.randint(0, 255)])
    return sync + ts_bytes + q_bytes + crc

def write_log(filepath, buffer):
    with open(filepath, 'w') as f:
        f.write("--- GROUND STATION RX LOG ---\n")
        f.write("STATUS: DEGRADED\n")
        idx = 0
        while idx < len(buffer):
            chunk_size = random.randint(3, 12)
            chunk = buffer[idx:idx+chunk_size]
            hex_str = ' '.join(f'{b:02X}' for b in chunk)
            f.write(f"[RX_DATA]: {hex_str}\n")
            # Inject some noise lines
            if random.random() < 0.2:
                f.write("[WARN]: PLL LOCK LOST\n")
            idx += chunk_size

def write_raw(filepath, buffer):
    with open(filepath, 'w') as f:
        hex_str = buffer.hex().upper()
        idx = 0
        while idx < len(hex_str):
            # Break randomly, which might split a hex pair across lines
            chunk_size = random.randint(15, 45)
            f.write(hex_str[idx:idx+chunk_size] + "\n")
            idx += chunk_size

def write_json(filepath, buffer):
    with open(filepath, 'w') as f:
        frames = [f"{b:02X}" for b in buffer]
        # Wrap it in nested noise
        data = {
            "metadata": {"station_id": "G-04", "status": "PARTIAL_LOSS"},
            "telemetry": {"frames": frames}
        }
        json.dump(data, f, indent=2)

def build_env():
    os.makedirs("telemetry_dumps", exist_ok=True)
    os.makedirs("recovery", exist_ok=True)
    
    random.seed(8600)
    base_ts = 1730000000
    global_ts_set = set()
    
    # Generate 300 files spread across a nested tree
    for file_idx in range(300):
        sector = random.randint(1, 8)
        station = random.choice(['alpha', 'beta', 'gamma', 'delta'])
        folder = f"telemetry_dumps/sector_{sector}/station_{station}"
        os.makedirs(folder, exist_ok=True)
        
        fmt = random.choice(['log', 'raw', 'json', 'noise', 'noise'])
        
        # Noise decoy files
        if fmt == 'noise':
            ext = random.choice(['.xml', '.tmp', '.dat', '.txt'])
            with open(f"{folder}/decoy_{file_idx}{ext}", 'w') as f:
                if ext == '.xml':
                    f.write('<?xml version="1.0"?><error>Sync lost at 1A CF FC 1D. Unrecoverable.</error>')
                else:
                    f.write(''.join(chr(random.randint(32, 126)) for _ in range(100)))
            continue

        filepath = f"{folder}/downlink_{file_idx}.{fmt}"
        
        # Base random byte noise for the file buffer
        buffer_len = random.randint(50, 200)
        buffer = bytearray(os.urandom(buffer_len))
        
        # Inject 1 to 4 packets
        num_packets = random.randint(1, 4)
        for _ in range(num_packets):
            is_valid = random.random() < 0.4  # 40% chance to be valid
            
            ts = base_ts + random.randint(1, 86400)
            while ts in global_ts_set:
                ts = base_ts + random.randint(1, 86400)
            global_ts_set.add(ts)
            
            pkt = make_packet(is_valid, ts)
            
            # Insert packet at random position in the buffer
            insert_pos = random.randint(0, len(buffer))
            buffer[insert_pos:insert_pos] = pkt
            
        if fmt == 'log':
            write_log(filepath, buffer)
        elif fmt == 'raw':
            write_raw(filepath, buffer)
        elif fmt == 'json':
            write_json(filepath, buffer)

if __name__ == "__main__":
    build_env()
