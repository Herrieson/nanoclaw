import os
import pandas as pd
import json
import random
import datetime

def build_env():
    # Base directory
    base_dir = "archive_v3_final_final"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create Master Lease List in a deep subfolder
    lease_dir = os.path.join(base_dir, "legal/contracts/active")
    os.makedirs(lease_dir, exist_ok=True)
    master_data = {
        "TenantName": ["John Smith", "Alice Johnson", "Robert Brown", "Emily Davis", "Michael Wilson", "Sarah Miller", "David Chen", "Laura White"],
        "Unit": ["101", "102", "103", "201", "202", "203", "301", "302"],
        "ExpectedMonthlyRent": [1200, 1500, 1100, 1800, 1350, 1600, 2000, 1750]
    }
    df_master = pd.DataFrame(master_data)
    df_master.to_csv(os.path.join(lease_dir, "master_leases.csv"), index=False)

    # 2. Generate the "Waste" - 200+ decoy files
    noise_dirs = ["temp_dumps", "backups/v1", "backups/v2", "recovery_bin", "legacy_data/2022"]
    for nd in noise_dirs:
        path = os.path.join(base_dir, nd)
        os.makedirs(path, exist_ok=True)
        for i in range(40):
            fname = f"log_fragment_{random.randint(1000, 9999)}.txt"
            with open(os.path.join(path, fname), "w") as f:
                f.write("STATUS: VOID\n")
                f.write("RECOVERY_ERROR: DATA CORRUPTED\n")
                f.write(f"Seed_{random.random()}: {random.randint(0,100)}\n")

    # 3. Generate Valid Data Fragments (The "Truth")
    # Rule: Real files have "VERIFIED_LOG" in the first line
    
    # Month 1: Jan - Split into two CSVs
    m1_dir = os.path.join(base_dir, "fragments/q1/jan")
    os.makedirs(m1_dir, exist_ok=True)
    
    jan_part1 = [["John Smith", 1200], ["Alice Johnson", 1500], ["Robert Brown", 1100], ["Emily Davis", 1800]]
    df_jan1 = pd.DataFrame(jan_part1, columns=["tenant_id_name", "amount_paid"])
    with open(os.path.join(m1_dir, "jan_pt1.csv"), "w") as f:
        f.write("VERIFIED_LOG | TIMESTAMP: 2024-01-31\n")
        df_jan1.to_csv(f, index=False)

    jan_part2 = [["Michael Wilson", 1350], ["Sarah Miller", 1600], ["David Chen", 2000], ["Laura White", 1750]]
    df_jan2 = pd.DataFrame(jan_part2, columns=["tenant_id_name", "amount_paid"])
    with open(os.path.join(m1_dir, "jan_pt2.csv"), "w") as f:
        f.write("VERIFIED_LOG | TIMESTAMP: 2024-01-31\n")
        df_jan2.to_csv(f, index=False)

    # Month 2: Feb - JSON format with discrepancies
    m2_dir = os.path.join(base_dir, "fragments/q1/feb")
    os.makedirs(m2_dir, exist_ok=True)
    # Robert Brown underpaid (800 vs 1100), Ghost "Unknown_Entity_X" paid 400
    feb_data = [
        {"payee": "John Smith", "credit": 1200}, {"payee": "Alice Johnson", "credit": 1500},
        {"payee": "Robert Brown", "credit": 800}, {"payee": "Emily Davis", "credit": 1800},
        {"payee": "Michael Wilson", "credit": 1350}, {"payee": "Sarah Miller", "credit": 1600},
        {"payee": "David Chen", "credit": 2000}, {"payee": "Laura White", "credit": 1750},
        {"payee": "Unknown_Entity_X", "credit": 400}
    ]
    with open(os.path.join(m2_dir, "february_data.json"), "w") as f:
        # No header in JSON, but we'll add a separate metadata file in the same folder
        json.dump(feb_data, f)
    with open(os.path.join(m2_dir, "metadata.txt"), "w") as f:
        f.write("VERIFIED_LOG\nTARGET: FEBRUARY")

    # Month 3: March - Mixed format (CSV) with missing tenant
    m3_dir = os.path.join(base_dir, "fragments/q1/mar")
    os.makedirs(m3_dir, exist_ok=True)
    # Emily Davis missed payment, Ghost "Zodiac_Alpha" paid 2200
    mar_content = "VERIFIED_LOG | AUTH: SECURE\nName,Paid\n"
    mar_content += "John Smith,1200\nAlice Johnson,1500\nRobert Brown,1100\nMichael Wilson,1350\nSarah Miller,1600\nDavid Chen,2000\nLaura White,1750\nZodiac_Alpha,2200"
    with open(os.path.join(m3_dir, "mar_final.csv"), "w") as f:
        f.write(mar_content)

if __name__ == "__main__":
    build_env()
