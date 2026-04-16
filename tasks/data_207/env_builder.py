import os
import struct
import sqlite3
import random

def build_env():
    base_path = "assets/data_207"
    os.makedirs(base_path, exist_ok=True)

    # 1. Generate corrupted binary log
    # Format: 17 bytes VIN, 5 bytes Error Code, 4 bytes Timestamp (Little Endian)
    vin = b"1B74VINTAGEREST01"
    error_code = b"P0171" # System Too Lean
    timestamp = 1672531200
    
    with open(os.path.join(base_path, "corrupted_log.bin"), "wb") as f:
        # Write some junk header
        f.write(os.urandom(64))
        # Write valid record
        f.write(vin)
        f.write(error_code)
        f.write(struct.pack("<I", timestamp))
        # Write more junk
        f.write(os.urandom(128))

    # 2. Generate local TSB database
    db_path = os.path.join(base_path, "shop_manuals.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE tsb (id TEXT, code TEXT, description TEXT, fix TEXT)")
    tsbs = [
        ("TSB-99-01", "P0171", "System Too Lean (Bank 1)", "Check for vacuum leaks near the intake manifold and inspect O2 sensor voltage."),
        ("TSB-99-02", "P0300", "Random Misfire", "Replace spark plugs and check ignition coils."),
        ("TSB-99-03", "P0420", "Catalyst Efficiency", "Replace catalytic converter.")
    ]
    cursor.executemany("INSERT INTO tsb VALUES (?,?,?,?)", tsbs)
    conn.commit()
    conn.close()

    # 3. Generate OBD-II data stream (Text based log)
    # Target: Sensor 1 average voltage
    with open(os.path.join(base_path, "obd_stream.txt"), "w") as f:
        f.write("Timestamp,Sensor,Value\n")
        for i in range(100):
            sensor = "Sensor 1" if i % 2 == 0 else "Sensor 2"
            # Simulate a lean condition: voltage stays low (0.1 - 0.3V)
            val = round(random.uniform(0.1, 0.25), 3) if sensor == "Sensor 1" else round(random.uniform(0.4, 0.6), 3)
            f.write(f"{1000+i},{sensor},{val}\n")

    print(f"Environment for data_207 built successfully at {base_path}")

if __name__ == "__main__":
    build_env()
