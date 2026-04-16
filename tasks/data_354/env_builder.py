import os
import random
import shutil

def main():
    base_dir = "assets/data_354/work_logs"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    os.makedirs(base_dir, exist_ok=True)
    
    transformers = [
        {"id": "TX-102", "status": "active", "cost": 150.00, "sector": "north_sector"},
        {"id": "TX-109", "status": "decommissioned", "cost": 450.50, "sector": "north_sector"},
        {"id": "TX-115", "status": "maintenance", "cost": 75.25, "sector": "north_sector"},
        {"id": "TX-204", "status": "decommissioned", "cost": 1200.00, "sector": "east_sector/sub_a"},
        {"id": "TX-288", "status": "active", "cost": 0.00, "sector": "east_sector/sub_b"},
        {"id": "TX-301", "status": "pending", "cost": 310.00, "sector": "west_sector"},
        {"id": "TX-404", "status": "active", "cost": 15.50, "sector": "south_sector"},
        {"id": "TX-501", "status": "decommissioned", "cost": 325.25, "sector": "south_sector/old_yard"},
        {"id": "TX-512", "status": "maintenance", "cost": 500.00, "sector": "south_sector/old_yard"},
        {"id": "TX-600", "status": "active", "cost": 42.10, "sector": "central_hub"}
    ]
    
    notes_templates = [
        "Routine check completed. No major issues.",
        "Oil leak detected, repaired seal.",
        "Unit beyond repair. Needs to be replaced.",
        "Replaced blown fuse.",
        "Voltage fluctuations observed. Needs further monitoring."
    ]

    for t in transformers:
        sector_dir = os.path.join(base_dir, t["sector"])
        os.makedirs(sector_dir, exist_ok=True)
        
        file_path = os.path.join(sector_dir, f"report_{t['id'].lower().replace('-', '_')}.log")
        
        content = f"""=== Inspection Log ===
Inspector: [REDACTED]
Date: 2022-10-14
Transformer ID: {t['id']}
Location: {t['sector'].upper()}
Status: {t['status']}
Repair Cost: ${t['cost']:.2f}
Notes: {random.choice(notes_templates)}
======================
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    main()
