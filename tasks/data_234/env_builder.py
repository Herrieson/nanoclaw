import os
import sqlite3
import binascii

def build_env():
    base_dir = "assets/data_234"
    cam_logs_dir = os.path.join(base_dir, "cam_logs")
    
    os.makedirs(cam_logs_dir, exist_ok=True)
    
    # 1. Create Hex-encoded log files
    logs = {
        "log_A.dat": [
            "2023-11-04 06:10:00 - Event: Raccoon",
            "2023-11-05 05:45:00 - Event: Buck",
            "2023-11-05 08:20:00 - Event: Doe"
        ],
        "log_B.dat": [
            "2023-11-06 14:00:00 - Event: Squirrel",
            "2023-11-06 17:30:00 - Event: Buck",
            "2023-11-07 06:00:00 - Event: Turkey"
        ]
    }
    
    for filename, lines in logs.items():
        filepath = os.path.join(cam_logs_dir, filename)
        with open(filepath, "w") as f:
            for line in lines:
                # Convert string to hex
                hex_str = binascii.hexlify(line.encode('utf-8')).decode('utf-8')
                f.write(hex_str + "\n")
                
    # 2. Create SQLite Weather Database
    db_path = os.path.join(base_dir, "weather.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temp_f INTEGER NOT NULL
        )
    ''')
    
    # Insert weather data (including the targets and some noise)
    weather_data = [
        ("2023-11-04 06:10:00", 35),
        ("2023-11-05 05:00:00", 30),
        ("2023-11-05 05:45:00", 28), # Target 1
        ("2023-11-05 08:20:00", 34),
        ("2023-11-06 14:00:00", 45),
        ("2023-11-06 17:30:00", 31), # Target 2
        ("2023-11-07 06:00:00", 29)
    ]
    
    cursor.executemany('INSERT INTO readings (timestamp, temp_f) VALUES (?, ?)', weather_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
