import os
import sqlite3
import csv
import math

def setup_environment():
    asset_dir = "assets/data_324"
    os.makedirs(asset_dir, exist_ok=True)
    
    # 1. Create SQLite DB
    db_path = os.path.join(asset_dir, "history_sites.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE landmarks (
            id INTEGER PRIMARY KEY,
            name TEXT,
            lat REAL,
            lon REAL,
            description TEXT
        )
    """)
    
    landmarks = [
        (1, "Old Settler's Cabin", 39.4201, -82.5301, "A restored 19th-century log cabin built by early Ohio pioneers."),
        (2, "Abandoned Coal Mine", 39.4251, -82.5351, "Remnants of an early 1900s coal mining operation that respected the surrounding forest."),
        (3, "Whispering Falls", 39.4280, -82.5400, "A beautiful seasonal waterfall cascading over sandstone cliffs."),
        (4, "Ghost Town of Moonville", 39.5000, -82.6000, "An old abandoned railroad town, complete with a haunted tunnel. Too far for today's hike.")
    ]
    
    cursor.executemany("INSERT INTO landmarks VALUES (?, ?, ?, ?, ?)", landmarks)
    conn.commit()
    conn.close()
    
    # 2. Create CSV GPS Log
    csv_path = os.path.join(asset_dir, "trail_day_1.csv")
    
    # Trail route: Starts near Cabin, goes to Mine, goes to Falls
    route_points = [
        {"timestamp": "08:00:00", "lat": 39.4200, "lon": -82.5300}, # Near Cabin (distance ~15m)
        {"timestamp": "08:15:00", "lat": 39.4215, "lon": -82.5315},
        {"timestamp": "08:30:00", "lat": 39.4230, "lon": -82.5330},
        {"timestamp": "08:45:00", "lat": 39.4250, "lon": -82.5350}, # Near Mine (distance ~15m)
        {"timestamp": "09:00:00", "lat": 39.4265, "lon": -82.5375},
        {"timestamp": "09:15:00", "lat": 39.4281, "lon": -82.5402}, # Near Falls (distance ~20m)
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "lat", "lon"])
        writer.writeheader()
        writer.writerows(route_points)

if __name__ == "__main__":
    setup_environment()
