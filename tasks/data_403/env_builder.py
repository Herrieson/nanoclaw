import os
import json
import base64
import uuid
import shutil

def build_env():
    # Define paths
    base_dir = "assets/data_403"
    records_dir = os.path.join(base_dir, "vintage_records")
    
    # Clean and create directories
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(records_dir, exist_ok=True)

    # The record collection data
    records = [
        {"artist": "Miles Davis", "album": "Kind of Blue", "genre": "Jazz", "year": 1959, "price": 50},
        {"artist": "Marvin Gaye", "album": "What's Going On", "genre": "Soul", "year": 1971, "price": 40},
        {"artist": "Michael Jackson", "album": "Thriller", "genre": "Pop", "year": 1982, "price": 30},
        {"artist": "John Coltrane", "album": "A Love Supreme", "genre": "Jazz", "year": 1965, "price": 60},
        {"artist": "Aretha Franklin", "album": "Lady Soul", "genre": "Soul", "year": 1968, "price": 45},
        {"artist": "Pink Floyd", "album": "Dark Side of the Moon", "genre": "Rock", "year": 1973, "price": 55},
        {"artist": "Stevie Wonder", "album": "Songs in the Key of Life", "genre": "Soul", "year": 1976, "price": 35},
        {"artist": "Thelonious Monk", "album": "Brilliant Corners", "genre": "Jazz", "year": 1957, "price": 70},
        {"artist": "Curtis Mayfield", "album": "Superfly", "genre": "Soul", "year": 1972, "price": 38},
        {"artist": "Herbie Hancock", "album": "Head Hunters", "genre": "Jazz", "year": 1973, "price": 42},
        {"artist": "Nina Simone", "album": "Baltimore", "genre": "Jazz", "year": 1978, "price": 25}
    ]

    # Scramble: JSON -> String -> Base64 -> save to random UUID file
    for record in records:
        json_str = json.dumps(record)
        b64_encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        filename = f"{uuid.uuid4().hex[:12]}.dat"
        filepath = os.path.join(records_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(b64_encoded)

if __name__ == "__main__":
    build_env()
