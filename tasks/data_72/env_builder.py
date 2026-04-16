import os
import sqlite3
import hashlib
import random

def setup_environment():
    base_dir = "assets/data_72"
    dump_dir = os.path.join(base_dir, "submissions_dump")
    os.makedirs(dump_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "band_records.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables. Adding a decoy table to confuse slightly.
    cursor.execute("""
        CREATE TABLE legacy_submissions (
            id INTEGER PRIMARY KEY,
            hash_val TEXT,
            band TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE official_tracks (
            track_id INTEGER PRIMARY KEY,
            file_hash TEXT,
            band_name TEXT,
            song_title TEXT,
            duration INTEGER
        )
    """)
    
    # Generate mock data
    bands = [
        ("The Velvet Underground", "Sunday Morning"),
        ("Arctic Monkeys", "Do I Wanna Know"),
        ("Tame Impala", "Let It Happen"),
        ("The Strokes", "Reptilia"),
        ("Paramore", "Misery Business"),
        ("My Chemical Romance", "Welcome to the Black Parade")
    ]
    
    random.seed(42)
    valid_hashes = []
    
    for band, song in bands:
        # Create hash
        raw_str = f"{band}_{song}_{random.randint(100, 999)}"
        file_hash = hashlib.md5(raw_str.encode()).hexdigest()
        valid_hashes.append(file_hash)
        
        # Insert into official DB
        cursor.execute(
            "INSERT INTO official_tracks (file_hash, band_name, song_title, duration) VALUES (?, ?, ?, ?)",
            (file_hash, band, song, random.randint(120, 300))
        )
        
        # Create corresponding fake mp3 file in dump
        file_path = os.path.join(dump_dir, file_hash)
        with open(file_path, "wb") as f:
            f.write(b"ID3\x03\x00\x00\x00\x00\x00\x00")
            f.write(os.urandom(1024))
            
    # Add some decoy entries in the DB without files
    for i in range(3):
        fake_hash = hashlib.md5(f"fake_{i}".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO official_tracks (file_hash, band_name, song_title, duration) VALUES (?, ?, ?, ?)",
            (fake_hash, f"Fake Band {i}", f"Fake Song {i}", 180)
        )
        
    # Add some junk files in the dump
    for i in range(5):
        junk_hash = hashlib.md5(f"junk_{i}".encode()).hexdigest()
        file_path = os.path.join(dump_dir, junk_hash)
        with open(file_path, "w") as f:
            f.write("This is just a random text log file or system junk.")
            
    # Add a decoy table data
    cursor.execute("INSERT INTO legacy_submissions (hash_val, band) VALUES ('1234567890abcdef', 'Old Band')")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_environment()
    print("Environment setup complete for data_72.")
