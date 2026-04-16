import os
import sqlite3

def build_env():
    base_dir = "assets/data_10"
    os.makedirs(base_dir, exist_ok=True)

    # Create messy text file
    sightings_content = """2023-10-01|John Doe|American Robin|2
Weather was great today! Saw some cool things.
2023-10-02|Mary Jane|bald eagle|1
2023-10-02|Sue Smith|American Robin|1
We shouldn't count the pigeons but here they are
2023-10-03|Bob Builder|Rock Pigeon|5
2023-10-04|Alice|Mountain Bluebird|4
2023-10-04|John Doe|Red-Tailed Hawk|2
2023-10-05|Mary Jane|american robin|4
Forgot my glasses today, might have misidentified some.
2023-10-06|Dave|European Starling|3
2023-10-07|Eve|Mountain Bluebird|1
"""
    with open(os.path.join(base_dir, "volunteer_sightings.txt"), "w") as f:
        f.write(sightings_content)

    # Create SQLite database
    db_path = os.path.join(base_dir, "utah_birds.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE birds (
        id INTEGER PRIMARY KEY,
        common_name TEXT NOT NULL,
        is_native INTEGER NOT NULL,
        conservation_status TEXT NOT NULL
    )
    """)

    birds_data = [
        ("American Robin", 1, "Least Concern"),
        ("Bald Eagle", 1, "Least Concern"),
        ("Rock Pigeon", 0, "Least Concern"),
        ("Mountain Bluebird", 1, "Least Concern"),
        ("Red-tailed Hawk", 1, "Least Concern"),
        ("European Starling", 0, "Least Concern"),
        ("Peregrine Falcon", 1, "Least Concern")
    ]
    
    cursor.executemany("INSERT INTO birds (common_name, is_native, conservation_status) VALUES (?, ?, ?)", birds_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
