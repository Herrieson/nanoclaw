import os
import random
import json

def build_env():
    # 🚨 Execute in the current working directory: assets/data_round_01_aligned_mix_800_0501/
    base_dir = "archivos_del_caos"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create a massive deeply nested structure to hide data
    sub_dirs = ["temp", "backups", "old_logs", "recovered", "trash", "exports/v1", "exports/v2", "sync_data"]
    for d in sub_dirs:
        os.makedirs(os.path.join(base_dir, d), exist_ok=True)

    # 2. Generate NOISE: 200+ useless files
    for i in range(200):
        folder = random.choice(sub_dirs)
        filename = f"record_{i:03d}.json" if i % 2 == 0 else f"note_{i:03d}.txt"
        with open(os.path.join(base_dir, folder, filename), "w") as f:
            f.write(f"Garbage data {random.random()}\nProject: Summer_Picnic_2023\nStatus: Archived")

    # 3. Hidden "Truth" - Fragmented Core Data
    # Piece 1: The valid Donation List (Mixed with cancelled ones)
    # Location: deep in exports/v2/
    donations_path = os.path.join(base_dir, "exports/v2", "donations_manifest_2024.csv")
    with open(donations_path, "w") as f:
        f.write("id,contributor,amount,type,verification_code\n")
        f.write("D001,Juan_Construction,1500,Check,V_OK_99\n") # Real
        f.write("D002,Pedro_Lies,500,Cash,V_FAIL_01\n")      # Fake
        f.write("D003,Carlos_Strong,800,Transfer,V_OK_42\n") # Real
        f.write("D004,Mateo_Ghost,300,Pledge,V_PENDING\n")    # Fake
        f.write("D005,Miguel_Angel,2200,Check,V_OK_11\n")    # Real
        f.write("D006,Hector_The_Great,4000,Cash,V_OK_88\n") # Real
        f.write("D007,Luis_Late,100,Cash,V_FAIL_02\n")       # Fake

    # Piece 2: The "Verification Key" (Multi-hop requirement)
    # Hidden in a semi-structured log file in 'sync_data'
    with open(os.path.join(base_dir, "sync_data", "system_messages.log"), "w") as f:
        f.write("[INFO] System boot...\n")
        f.write("[DATA] Integrity Check: Files with 'V_OK' codes are verified by the bank.\n")
        f.write("[DATA] Warning: 'V_FAIL' or 'PENDING' are bounced or unconfirmed. DO NOT COUNT.\n")
        f.write("[INFO] Project Filter: Only records tagged with 'Mariachi Fund 2024' in the header are valid for the church project.\n")

    # Piece 3: The Expense Fragment (JSON format)
    # Hidden in 'old_logs' but it's the only one with the 2024 tag
    expense_data = {
        "metadata": {
            "project": "Mariachi Fund 2024",
            "fiscal_year": 2024
        },
        "line_items": [
            {"item": "Mariachi Band Deposit", "cost": 1200, "approved": True},
            {"item": "Sound System Rental", "cost": 450, "approved": True},
            {"item": "Emergency Beer (Unauthorized)", "cost": 200, "approved": False},
            {"item": "Street Permit (PAID BY CHURCH ACCOUNT)", "cost": 50, "internal_transfer": True}
        ]
    }
    with open(os.path.join(base_dir, "old_logs", "summary_v99_final.json"), "w") as f:
        json.dump(expense_data, f)

    # 4. Decoy Data (Looks real but is wrong)
    decoy_expense = {
        "metadata": {"project": "Summer_Picnic_2023"},
        "line_items": [{"item": "Hotdogs", "cost": 5000, "approved": True}]
    }
    with open(os.path.join(base_dir, "temp", "expenses_draft.json"), "w") as f:
        json.dump(decoy_expense, f)

if __name__ == "__main__":
    build_env()
