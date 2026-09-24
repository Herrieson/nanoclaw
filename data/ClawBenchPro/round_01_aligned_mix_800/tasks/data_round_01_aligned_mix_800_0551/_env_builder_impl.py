import os
import json
import random

def build_env():
    root = "archive_S7"
    os.makedirs(root, exist_ok=True)

    # 1. Create the master metadata (The "Key" to the puzzle)
    active_work_id = "WID-9921-X"
    target_week = "2023-W42"
    with open(os.path.join(root, "metadata.json"), "w") as f:
        json.dump({
            "status": "OPERATIONAL",
            "active_project_id": active_work_id,
            "reporting_period": target_week,
            "note": "Filter all logs by active_project_id. Ignore legacy data."
        }, f, indent=4)

    # 2. Create a fragmented directory structure
    sub_dirs = ["logs/daily", "logs/backup", "finance/receipts", "finance/drafts", "raw_data/temp"]
    for d in sub_dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)

    # 3. Generate Noise/Decoy Files (Scale Simulation: 500+ files)
    for i in range(500):
        # Random decoys
        folder = random.choice(sub_dirs)
        ext = random.choice([".log", ".txt", ".dat", ".tmp"])
        with open(os.path.join(root, folder, f"old_record_{i}{ext}"), "w") as f:
            f.write(f"DECOY DATA: Project WID-{random.randint(1000, 8000)}. Status: Irrelevant.")

    # 4. Generate the TRUE Violation Fragments (Scattered)
    # Fragment 1: The JSON audit
    violation_1 = {
        "meta": {"pid": active_work_id, "timestamp": "2023-10-16T09:00:00"},
        "observations": ["Exposed high-voltage wiring in Section 4", "No fire extinguisher at welding station"]
    }
    with open(os.path.join(root, "logs/daily/audit_part_A.json"), "w") as f:
        json.dump(violation_1, f)

    # Fragment 2: The Text log
    with open(os.path.join(root, "logs/backup/site_notes_final.log"), "w") as f:
        f.write(f"LOG_START | ID: {active_work_id} | DATE: 2023-10-18\n")
        f.write("Note: Found workers operating forklift without certification. Serious violation.\n")
        f.write("Note: Scaffolding missing toe-boards on North face.\n")
        f.write("LOG_END")

    # 5. Generate the TRUE Expenses (Buried in finance)
    true_expenses = [
        ("Fire Suppression Kit", 450.00),
        ("Hard Hat Bulk Pack", 210.50),
        ("Safety Harnesses (x5)", 875.00),
        ("First Aid Station Refill", 65.25)
    ]
    
    # Mix true expenses with art decoys in a high-volume folder
    for i, (item, cost) in enumerate(true_expenses):
        filename = f"trans_772{i}.dat"
        with open(os.path.join(root, "finance/receipts", filename), "w") as f:
            f.write(f"TYPE: TRANSACTION\nPROJECT: {active_work_id}\nITEM: {item}\nCATEGORY: SAFETY_SECURE\nAMOUNT: {cost}\nSTATUS: PAID")

    # Add 100 Art Supply decoys
    art_items = ["Oil Paint Set", "Marble Slab", "Chisels", "Large Canvas", "Turpentine"]
    for i in range(100):
        item = random.choice(art_items)
        cost = random.uniform(20.0, 500.0)
        with open(os.path.join(root, "finance/receipts", f"art_expense_{i}.dat"), "w") as f:
            f.write(f"TYPE: TRANSACTION\nPROJECT: {active_work_id}\nITEM: {item}\nCATEGORY: ART_SUPPLY\nAMOUNT: {cost:.2f}\nSTATUS: PAID")

if __name__ == "__main__":
    build_env()
