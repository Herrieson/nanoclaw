import os
import random
import struct

def build_env():
    workspace_dir = "assets/data_226/workspace"
    os.makedirs(workspace_dir, exist_ok=True)
    
    log_file_path = os.path.join(workspace_dir, "bike_telemetry.log")
    
    # Starting timestamp
    base_ts = 1700000000000
    
    lines = []
    
    # Generate some normal data
    for i in range(50):
        ts = base_ts + i * 10
        imu_x = random.randint(-100, 100)
        imu_y = random.randint(-50, 50)
        imu_z = random.randint(950, 1050) # roughly 1g gravity
        power = random.randint(100, 300)
        
        # Pack as little-endian: h = short (2 bytes signed), H = unsigned short (2 bytes unsigned)
        payload = struct.pack('<hhhH', imu_x, imu_y, imu_z, power)
        lines.append(f"{ts},{payload.hex().upper()}")

    # INJECT TRAP: High power, but IMU_X is low (stationary sprint / trainer)
    trap_ts = base_ts + 550
    payload_trap = struct.pack('<hhhH', 100, 0, 1000, 1200) # 1200W, but only 100mg
    lines.append(f"{trap_ts},{payload_trap.hex().upper()}")

    # INJECT TARGET: Max power where IMU_X > 500
    target_ts = base_ts + 600
    payload_target = struct.pack('<hhhH', 650, 20, 980, 850) # 850W, 650mg
    lines.append(f"{target_ts},{payload_target.hex().upper()}")

    # INJECT NOISE: Another > 500 IMU_X but lower power
    noise_ts = base_ts + 650
    payload_noise = struct.pack('<hhhH', 550, -10, 990, 700) # 700W, 550mg
    lines.append(f"{noise_ts},{payload_noise.hex().upper()}")

    # Generate more normal data
    for i in range(70, 100):
        ts = base_ts + i * 10
        imu_x = random.randint(-100, 100)
        imu_y = random.randint(-50, 50)
        imu_z = random.randint(950, 1050)
        power = random.randint(100, 300)
        
        payload = struct.pack('<hhhH', imu_x, imu_y, imu_z, power)
        lines.append(f"{ts},{payload.hex().upper()}")

    with open(log_file_path, "w") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    build_env()
