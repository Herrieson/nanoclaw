import os
import sqlite3
import base64
import json

def build():
    base_path = "assets/data_467"
    os.makedirs(f"{base_path}/maintenance", exist_ok=True)
    os.makedirs(f"{base_path}/data/chunks", exist_ok=True)

    # 1. Create a "broken" obfuscation script
    obfuscator_code = """
import base64
import sys

def decode_data(encoded_str):
    # Brenda's "security": just base64 followed by reversing the string
    return base64.b64decode(encoded_str[::-1]).decode('utf-8')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No data provided")
        sys.exit(1)
    # Hint: Brenda forgot she needs a specific library or the logic is slightly flipped
    print(decode_data(sys.argv[1]))
"""
    with open(f"{base_path}/maintenance/obfuscator.py", "w") as f:
        f.write(obfuscator_code)

    # 2. Create the fragmented data (Chunks)
    # Supplier: Cactus Wonders Inc.
    # Total Amount: $4,520.50
    # PO Hash: AZ-9982X-CW
    suppliers = [
        {"name": "Cactus Wonders Inc.", "amount": 4520.50, "po_hash": "AZ-9982X-CW", "stock": 50},
        {"name": "Desert Trinkets", "amount": 1200.00, "po_hash": "DT-1122", "stock": 12},
        {"name": "Grand Canyon Mugs", "amount": 850.00, "po_hash": "GC-5541", "stock": 8},
        {"name": "Phoenix Postcards", "amount": 300.25, "po_hash": "PP-0091", "stock": 105}
    ]

    for i, s in enumerate(suppliers):
        raw_str = json.dumps(s)
        # Brenda's "obfuscation" logic: reverse then base64
        encoded = base64.b64encode(raw_str.encode('utf-8')).decode('utf-8')[::-1]
        with open(f"{base_path}/data/chunks/chunk_{i}.dat", "w") as f:
            f.write(encoded)

    # 3. Leave a "messy" note
    with open(f"{base_path}/todo_note.txt", "w") as f:
        f.write("Note to self: The chunks are encoded using the script in maintenance. Check all .dat files. The boss wants the low-stock-report.csv by tonight!")

if __name__ == "__main__":
    build()
