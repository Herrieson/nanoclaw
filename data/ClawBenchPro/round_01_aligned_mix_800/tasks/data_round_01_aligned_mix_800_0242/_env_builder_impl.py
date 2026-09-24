import os
import json
import base64

def build_env():
    # Create the evidence directories
    os.makedirs("evidence/transactions", exist_ok=True)
    
    # 1. Create the suspect aliases (Agent must resolve these)
    # Target 1: NIGHTHAWK -> ACC-1001-XYZ (Total: 7000)
    # Target 2: SILVERFOX -> ACC-2002-ABC (Total: 8050)
    aliases = ["CODENAME: NIGHTHAWK", "CODENAME: SILVERFOX"]
    with open("evidence/suspect_aliases.txt", "w") as f:
        for a in aliases:
            f.write(f"{a}\n")

    # 2. Create Encrypted Ledgers (Simple Base64 to simulate proprietary format)
    # Ledger Q1
    q1_data = [
        {"tx_id": "tx-8921", "src": "ACC-CORP-99", "dst": "ACC-1001-XYZ", "amt": 5400.00, "status": "CLEARED"},
        {"tx_id": "tx-8922", "src": "ACC-RETAIL-1", "dst": "ACC-9999-FOO", "amt": 1200.50, "status": "CLEARED"},
        {"tx_id": "tx-8923", "src": "ACC-HOLDING-2", "dst": "ACC-2002-ABC", "amt": 8000.00, "status": "CLEARED"}
    ]
    # Ledger Q2
    q2_data = [
        {"tx_id": "tx-9001", "amt": 1100.00, "src": "ACC-CORP-88", "dst": "ACC-1001-XYZ"},
        {"tx_id": "tx-9002", "amt": 300.00, "src": "ACC-RETAIL-1", "dst": "ACC-8888-BAR"},
        {"tx_id": "tx-9003", "amt": 50.00, "src": "ACC-CORP-99", "dst": "ACC-2002-ABC"},
        {"tx_id": "tx-9004", "amt": 500.00, "src": "ACC-HOLDING-2", "dst": "ACC-1001-XYZ"}
    ]

    def save_enc(data, filename):
        raw_str = json.dumps(data)
        encoded = base64.b64encode(raw_str.encode()).decode()
        with open(f"evidence/transactions/{filename}.swift_enc", "w") as f:
            f.write(f"---BEGIN SWIFT ENCRYPTED BLOCK---\n{encoded}\n---END SWIFT ENCRYPTED BLOCK---")

    save_enc(q1_data, "ledger_Q1")
    save_enc(q2_data, "ledger_Q2")

if __name__ == "__main__":
    build_env()
