import os
import json
import csv
import random

def setup_environment():
    base_path = "assets/data_295"
    os.makedirs(base_path, exist_ok=True)

    # 1. Create a "corrupted" CSV inventory
    inventory_file = os.path.join(base_path, "inventory_partial.csv")
    inventory_data = [
        ["batch_id", "product_name", "status", "last_seen_hub"],
        ["290", "Soft-Touch-V1", "Delivered", "CLE-1"],
        ["295", "Active-Glow-TX1", "Transit-Error", "ERR_REDIRECT"],
        ["301", "Thermal-Mesh", "Warehouse", "CIN-2"]
    ]
    with open(inventory_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # 2. Create raw system logs with clues
    log_file = os.path.join(base_path, "system_raw.log")
    logs = [
        "2023-10-27 08:00:01 INFO: System Booting...",
        "2023-10-27 09:15:22 WARN: Database connection latency detected.",
        "2023-10-27 10:05:44 TRACE: Batch 295 detected at Node: HUB-COL-77.",
        "2023-10-27 10:06:10 ERROR: Routing failed for Batch 295. Internal Code: 0x4B3A2D.",
        "2023-10-27 11:00:00 INFO: Diverting Batch 295 to secure overflow facility: WAREHOUSE-99-X.",
        "2023-10-27 11:05:12 DEBUG: Container Assigned: [ENCODED_ID: 0x1D141C1B101D].",
    ]
    with open(log_file, 'w') as f:
        f.write("\n".join(logs))

    # 3. Create the diagnostic config file with the XOR key
    # Logic: Encoded 0x1D141C1B101D XOR Key 'FASHION' (truncated/repeated)
    # Let's use a simpler key for a 50-year-old's tech environment: "FABRIC"
    # F(46) A(41) B(42) R(52) I(49) C(43)
    config_file = os.path.join(base_path, "config.local")
    config_content = """
# 3PL System Diagnostics - v2.4.1
# Security Settings
OBFUSCATION_KEY=FABRIC
LOG_LEVEL=DEBUG
# Network Config
LOCAL_GATEWAY=192.168.1.254
    """
    with open(config_file, 'w') as f:
        f.write(config_content)

if __name__ == "__main__":
    setup_environment()
