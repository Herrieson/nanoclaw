import os
import sqlite3
import gzip
import random
import csv
from datetime import datetime, timedelta

def build_env():
    base_dir = "assets/data_399"
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "sensors.db")
    
    # 1. Create SQLite Database for Sensor Metadata
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE sensors (
            sensor_id TEXT PRIMARY KEY,
            location_zone TEXT,
            install_date TEXT
        )
    """)
    
    sensors = [
        ("S-001", "North Pasture"),
        ("S-002", "South Pasture"),
        ("S-003", "Riparian Buffer Zone"), # Normal
        ("S-004", "East Orchard"),
        ("S-005", "Riparian Buffer Zone"), # Acidic anomaly
        ("S-006", "West Field"),
        ("S-007", "Main Crop Row A"),
        ("S-008", "Riparian Buffer Zone"), # Acidic anomaly
        ("S-009", "East Orchard"),         # Acidic anomaly (but wrong zone)
        ("S-010", "Main Crop Row B")
    ]
    
    for s_id, loc in sensors:
        cursor.execute("INSERT INTO sensors VALUES (?, ?, ?)", (s_id, loc, "2023-01-15"))
    conn.commit()
    conn.close()
    
    # 2. Generate Logs
    start_date = datetime(2023, 10, 1)
    
    for day_offset in range(31):
        current_date = start_date + timedelta(days=day_offset)
        filename = f"soil_readings_{current_date.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(logs_dir, filename)
        
        # Decide if this file should be gzipped (randomly to test file handling)
        compress = day_offset % 3 == 0
        if compress:
            filepath += ".gz"
            open_func = gzip.open
            mode = "wt"
        else:
            open_func = open
            mode = "w"
            
        with open_func(filepath, mode, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "sensor_id", "moisture_pct", "ph_level", "nitrogen_ppm"])
            
            for s_id, _ in sensors:
                # Base stats
                moisture = round(random.uniform(30.0, 60.0), 1)
                ph = round(random.uniform(6.5, 7.5), 2)
                nitrogen = round(random.uniform(10.0, 25.0), 1)
                
                # Inject anomalies
                if s_id == "S-005":
                    # Slow drop in pH
                    if day_offset > 20:
                        ph = round(random.uniform(5.4, 5.9), 2)
                        # Ensure we know the exact minimum for verification
                        if day_offset == 25: ph = 5.45
                elif s_id == "S-008":
                    if day_offset > 15:
                        ph = round(random.uniform(5.7, 5.99), 2)
                        if day_offset == 18: ph = 5.72
                elif s_id == "S-009":
                    # Acidic but wrong zone!
                    ph = round(random.uniform(4.5, 5.5), 2)
                    if day_offset == 10: ph = 4.88
                    
                timestamp = current_date.strftime('%Y-%m-%dT%H:00:00')
                writer.writerow([timestamp, s_id, moisture, ph, nitrogen])

if __name__ == "__main__":
    build_env()
