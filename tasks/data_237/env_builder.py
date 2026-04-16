import os
import sqlite3
import random

def build_env():
    base_dir = "assets/data_237"
    os.makedirs(base_dir, exist_ok=True)

    db_path = os.path.join(base_dir, "compounds.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    # 1. Create SQLite DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE registry (
            id TEXT PRIMARY KEY,
            smiles TEXT,
            molecular_weight REAL
        )
    ''')

    # Define the core compounds (winners and distractors)
    core_compounds = [
        # Winners
        ("CID-1042", "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5", 493.6),
        ("CID-8831", "CN1CCN(CC1)C2=CC=CC=C2NC(=O)C3=CC=C(C=C3)NC4=NC=CC(=N4)C5=CC=CC=C5", 400.5),
        ("CID-9910", "CC1=C(C=C(C=C1)NC(=O)C2=CC=CC=C2)NC3=NC=CC(=N3)C4=CN=CC=C4", 350.4),
        # Distractors
        ("CID-2001", "CC1=CC=CC=C1NC(=O)NC2=CC=CC=C2", 212.2), # Fails Tox
        ("CID-3002", "C1=CC=C(C=C1)C2=CC=CC=C2", 154.2),       # Fails Status
        ("CID-4003", "C1=CC=C(C=C1)O", 94.1)                  # Fails Aff
    ]

    # Add noise compounds
    for i in range(100):
        core_compounds.append((f"CID-9{i:03d}", f"C{i}H{i*2}O", 100.0 + i))

    cursor.executemany('INSERT INTO registry (id, smiles, molecular_weight) VALUES (?, ?, ?)', core_compounds)
    conn.commit()
    conn.close()

    # 2. Create Assay Log
    log_path = os.path.join(base_dir, "assay_results.log")
    
    log_entries = []
    # Winners
    log_entries.append("[INFO] Machine 01 - CID: CID-1042 | Aff: 12.5 nM | Tox: 0.2 | Status: STABLE - Processed securely.")
    log_entries.append("[INFO] Machine 03 - CID: CID-8831 | Aff: 24.1 nM | Tox: 0.8 | Status: STABLE - Processed securely.")
    log_entries.append("[INFO] Machine 02 - CID: CID-9910 | Aff: 45.0 nM | Tox: 0.5 | Status: STABLE - Processed securely.")
    # Distractors
    log_entries.append("[INFO] Machine 01 - CID: CID-2001 | Aff: 5.0 nM | Tox: 1.2 | Status: STABLE - Warning high tox.")
    log_entries.append("[INFO] Machine 04 - CID: CID-3002 | Aff: 8.5 nM | Tox: 0.1 | Status: UNSTABLE - Degraded in solution.")
    log_entries.append("[INFO] Machine 02 - CID: CID-4003 | Aff: 55.0 nM | Tox: 0.1 | Status: STABLE - Processed securely.")
    
    # Noise logs
    for i in range(100):
        aff = round(random.uniform(55.0, 200.0), 1)
        tox = round(random.uniform(1.1, 5.0), 1)
        status = random.choice(["STABLE", "UNSTABLE"])
        log_entries.append(f"[DEBUG] Machine {random.randint(1,5):02d} - CID: CID-9{i:03d} | Aff: {aff} nM | Tox: {tox} | Status: {status} - Routine check.")
        
        # Throw in some completely unformatted junk lines to test regex/parsing
        if random.random() < 0.1:
            log_entries.append(f"ERR_CONNECTION_RESET at module {random.randint(100,999)} - disregard previous reading")

    random.shuffle(log_entries)

    with open(log_path, "w") as f:
        f.write("\n".join(log_entries))

if __name__ == "__main__":
    build_env()
