import os
import sqlite3
import base64
import json

def setup_environment():
    base_dir = "assets/data_465/investments/raw_data/"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create a corrupted SQLite database
    db_path = os.path.join(base_dir, "vault.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE acquisitions (id INTEGER, item_name TEXT, genre TEXT, purchase_date TEXT, price REAL)''')
    data = [
        (1, 'Sol de Esperanza', 'Modern Latin American', '2023-10-12', 45000.0),
        (2, 'Abstracto Azul', 'Contemporary', '2023-11-05', 12000.0),
        (3, 'Ritmo de la Tierra', 'Modern Latin American', '2023-12-01', 0.0), # Price is "hidden" elsewhere
        (4, 'Sueños de Maíz', 'Modern Latin American', '2023-11-20', 38000.0)
    ]
    cursor.executemany('INSERT INTO acquisitions VALUES (?,?,?,?,?)', data)
    conn.commit()
    conn.close()

    # Intentionally corrupt the DB file by overwriting some bytes (not too much to be unfixable, but enough to fail simple read)
    with open(db_path, "r+b") as f:
        f.seek(100)
        f.write(b"\xff\xff\xff\xff")

    # 2. Create the obfuscated log file for the missing price
    # Missing price for 'Ritmo de la Tierra' is 65000.0
    # Obfuscation: Base64 -> Reverse
    price_str = "65000.0"
    b64_price = base64.b64encode(price_str.encode()).decode()
    obfuscated_price = b64_price[::-1]
    
    log_content = f"""
    2023-12-01 10:00:01 - INFO - Auction start for Lot 42
    2023-12-01 10:15:20 - TRACE - Item: Ritmo de la Tierra
    2023-12-01 10:15:25 - DEBUG - Internal_Price_Token: {obfuscated_price}
    2023-12-01 10:20:00 - INFO - Auction closed
    """
    with open(os.path.join(base_dir, "system_trace.log"), "w") as f:
        f.write(log_content)

    # 3. Create a secondary JSON for current valuations
    valuations = {
        "Sol de Esperanza": 52000.0,
        "Ritmo de la Tierra": 78000.0,
        "Sueños de Maíz": 41000.0,
        "Abstracto Azul": 13000.0
    }
    with open(os.path.join(base_dir, "current_valuations.json"), "w") as f:
        json.dump(valuations, f)

if __name__ == "__main__":
    setup_environment()
