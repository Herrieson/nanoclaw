import os
import sqlite3
import json
import base64

def setup_environment():
    base_path = "assets/data_379"
    os.makedirs(base_path, exist_ok=True)
    
    # 1. Create the encryption logic backup (the hint)
    # The encryption is a simple XOR with a fixed key 'LUMINA_SECURE'
    encryptor_code = """
def xor_cipher(data, key):
    return bytearray([b ^ key[i % len(key)] for i, b in enumerate(data)])

# Note: I used key = b"LUMINA_SECURE_2024"
"""
    with open(os.path.join(base_path, "encryptor_logic.py.bak"), "w") as f:
        f.write(encryptor_code)

    # 2. Create the encrypted financial summary
    financial_data = {
        "claimed_q3_revenue": 4500000.00,
        "reported_users": 150000,
        "burn_rate": 250000.00
    }
    key = b"LUMINA_SECURE_2024"
    raw_json = json.dumps(financial_data).encode()
    encrypted_data = bytearray([b ^ key[i % len(key)] for i, b in enumerate(raw_json)])
    
    with open(os.path.join(base_path, "financial_summary.enc"), "wb") as f:
        f.write(encrypted_data)

    # 3. Create the Mock Database (Billing)
    db_path = os.path.join(base_path, "lumina_billing.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE billing (id INTEGER, user_id TEXT, amount REAL, timestamp TEXT, status TEXT)")
    
    # Insert 1000 records. Total "Real" revenue will be around $1.2M, much lower than claimed $4.5M
    # Also include some 'failed' or 'pending' statuses to test filtering
    for i in range(1000):
        status = "SUCCESS" if i % 10 != 0 else "FAILED"
        cursor.execute("INSERT INTO billing VALUES (?, ?, ?, ?, ?)", 
                       (i, f"USER_{i:04d}", 1250.0, "2024-09-01", status))
    conn.commit()
    conn.close()

    # 4. Create Traffic Logs (Semi-structured)
    # 5000 lines of traffic. Only some represent real active sessions.
    with open(os.path.join(base_path, "traffic_logs.txt"), "w") as f:
        for i in range(5000):
            if i % 5 == 0:
                f.write(f"INFO [2024-09-15 10:00:{i%60:02d}] SESSION_START: user_id=USER_{i%1200:04d} ip=192.168.1.{i%255}\n")
            else:
                f.write(f"DEBUG [2024-09-15 10:00:{i%60:02d}] HEARTBEAT: node_{i%10} status=OK\n")

if __name__ == "__main__":
    setup_environment()
