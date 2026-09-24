import os
import random
import json

def build_env():
    # 🚨 Execution context: cwd is already assets/data_round_01_aligned_mix_800_0527/
    
    # Direction 1: Fragmentation & Nested Mess
    diag_root = "diagnostics/scans/archive/internal"
    os.makedirs(diag_root, exist_ok=True)
    
    # Create hundreds of decoy/noise files
    for i in range(150):
        folder = os.path.join(diag_root, f"batch_{i:03d}")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"temp_{random.randint(1000,9999)}.tmp"), "w") as f:
            f.write("TEMP DATA: Sensor signal noise " + str(random.random()))

    # Real data scattered and hidden
    # Target 1: P0300 (Engine Misfire)
    target_1_dir = os.path.join(diag_root, "batch_042")
    with open(os.path.join(target_1_dir, "session_final_99.json"), "w") as f:
        data = {
            "metadata": {"integrity_flag": "FINAL", "session_id": "99A"},
            "payload": {
                "vin": "1HG1234",
                "plate": "GHOST-88",
                "codes": ["P0113", "P0300", "P1221"]
            }
        }
        json.dump(data, f)

    # Target 2: P0420 (Catalytic) - Fragmented across two files
    target_2_dir = os.path.join(diag_root, "batch_088")
    with open(os.path.join(target_2_dir, "chunk_a.log"), "w") as f:
        f.write("SESSION_ID: 101B | INTEGRITY: FINAL | PLATE: RUST-01 | VIN: 2T12345 | STATUS: PARTIAL")
    with open(os.path.join(target_2_dir, "chunk_b.log"), "w") as f:
        f.write("SESSION_ID: 101B | CODES: [P0420, P0442] | STATUS: COMPLETE")

    # Target 3: P0300 & P0420 - Deeply nested and messy
    target_3_dir = os.path.join(diag_root, "batch_112/sub_proc/err")
    os.makedirs(target_3_dir, exist_ok=True)
    with open(os.path.join(target_3_dir, "raw_dump.txt"), "w") as f:
        f.write("--- LOG START ---\nTIMESTAMP: 2023-10-27\nFLAG: FINAL\nPLATE: NEON-X\nERROR_HEX: 0x50303030 (P0300 equivalent in some systems, but we look for literal string)\nACTUAL_CODE: P0300\n--- LOG END ---")

    # Decoys (Non-FINAL or wrong codes)
    with open(os.path.join(diag_root, "batch_001/session_01.json"), "w") as f:
        json.dump({"metadata": {"integrity_flag": "DRAFT"}, "payload": {"plate": "FAKE-1", "codes": ["P0300"]}}, f)

    # Direction 2: Inventory Chaos
    inv_dir = "logs/archive"
    os.makedirs(inv_dir, exist_ok=True)
    
    inventory_fragments = [
        "Received 50 Spark Plugs (NGK) from supplier.",
        "Used 4 Spark Plugs on the Honda.",
        "Inventory Check: 12 Bosch Spark Plugs found in bin B.",
        "Scrapped 2 Spark Plugs due to cracked porcelain.",
        "Found a box of Champion Spark Plugs: total 24.",
        "Note: Spark Plug count in cabinet is actually 10 (mislabeled as 15).", # The "10" is the truth
        "System update: subtract 5 Spark Plugs for shop use.",
        "Emergency stock: 8 more Spark Plugs (Denso) added to shelf."
    ]
    
    for i, fragment in enumerate(inventory_fragments):
        with open(os.path.join(inv_dir, f"snapshot_{i:02d}.txt"), "w") as f:
            f.write(fragment)
            # Add noise to files
            f.write("\nOther items: 10 Oil filters, 2 Tires, 150 Washers.")

    # Logic for Spark Plugs:
    # 50 - 4 + 12 - 2 + 24 + 10 - 5 + 8 = 93
    # Wait, the note says "actually 10 (mislabeled as 15)", so Agent must parse carefully.

if __name__ == "__main__":
    build_env()
