import os
import sqlite3
import pandas as pd
import json

def setup_environment():
    base_dir = "assets/data_232"
    os.makedirs(base_dir, exist_ok=True)

    # 1. 混乱的原始数据 (CSV with encoding issues and noise)
    # Using 'latin-1' to simulate encoding issues for a system expecting UTF-8
    artist_data = [
        {"name": "Boricua Soul", "genre": "Reggaeton", "label": "San Juan Records", "hometown": "San Juan"},
        {"name": "Ritmo de Sueño", "genre": "Indie Pop", "label": "Island Beats", "hometown": "Ponce"},
        {"name": "Fake Artist 1", "genre": "Noise", "label": "Ghost Label", "hometown": "Unknown"},
        {"name": "Cultura Callejera", "genre": "Hip Hop", "label": "San Juan Records", "hometown": "Carolina"},
        {"name": "Mar y Sol", "genre": "Salsa", "label": "Caribbean Flow", "hometown": "Mayagüez"},
    ]
    df = pd.DataFrame(artist_data)
    csv_path = os.path.join(base_dir, "raw_artists.csv")
    df.to_csv(csv_path, index=False, encoding='latin-1')

    # 2. 标签数据库 (Verified labels)
    db_path = os.path.join(base_dir, "labels_registry.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE verified_labels (label_name TEXT, status TEXT)")
    cursor.execute("INSERT INTO verified_labels VALUES ('San Juan Records', 'Verified')")
    cursor.execute("INSERT INTO verified_labels VALUES ('Island Beats', 'Verified')")
    cursor.execute("INSERT INTO verified_labels VALUES ('Caribbean Flow', 'Verified')")
    conn.commit()
    conn.close()

    # 3. 模拟服务器信息 (Mocking an API endpoint)
    # We'll create a JSON file that acts as the "API Response" source
    server_info = {
        "endpoint": "http://localhost:8080/vibe_score",
        "instructions": "The server is mocked. Read 'vibe_data.json' to simulate API calls.",
        "note": "Filter by artist name to get the 'score' field."
    }
    with open(os.path.join(base_dir, "server_info.txt"), "w") as f:
        json.dump(server_info, f, indent=4)

    vibe_data = {
        "Boricua Soul": 95,
        "Ritmo de Sueño": 88,
        "Cultura Callejera": 92,
        "Mar y Sol": 85,
        "Fake Artist 1": 10
    }
    with open(os.path.join(base_dir, "vibe_data.json"), "w") as f:
        json.dump(vibe_data, f)

    # 4. 一些额外的干扰日志
    with open(os.path.join(base_dir, "system.log"), "w") as f:
        f.write("DEBUG: Connection established to local database.\n")
        f.write("ERROR: Failed to fetch data for Ghost Label - Record Not Found.\n")
        f.write("INFO: Data dump completed at 2023-10-27.\n")

if __name__ == "__main__":
    setup_environment()
