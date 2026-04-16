import os
import json
import random

def build_env():
    base_dir = "assets/data_484"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create supplier_catalog.json
    catalog = [
        {"Part_ID": "WLD-091", "Part_Name": "Heavy Duty Control Arm", "Base_Price": 250.00},
        {"Part_ID": "WLD-092", "Part_Name": "Standard Control Arm", "Base_Price": 150.00},
        {"Part_ID": "BRK-110", "Part_Name": "Brake Caliper Assembly", "Base_Price": 85.50},
        {"Part_ID": "SUS-404", "Part_Name": "Coilover Shock Absorber", "Base_Price": 420.00},
        {"Part_ID": "FRM-88X", "Part_Name": "Tubular Frame Gusset", "Base_Price": 45.00},
        {"Part_ID": "AXL-221", "Part_Name": "Rear Axle Shaft", "Base_Price": 310.00},
        {"Part_ID": "MNT-001", "Part_Name": "Engine Mount Bracket", "Base_Price": 65.00},
        {"Part_ID": "EXH-999", "Part_Name": "Titanium Exhaust Header", "Base_Price": 850.00},
        {"Part_ID": "STR-055", "Part_Name": "Steering Rack Pinion", "Base_Price": 195.00}
    ]
    
    with open(os.path.join(base_dir, "supplier_catalog.json"), "w") as f:
        json.dump(catalog, f, indent=4)

    # 2. Create noisy scanner_dump.txt
    # Target parts to be broken: SUS-404 (CRITICAL_FRACTURE), FRM-88X (NEEDS_WELDING), MNT-001 (CRITICAL_FRACTURE)
    
    log_lines = []
    statuses = ["STATUS: OK", "STATUS: MINOR_WEAR", "STATUS: CALIBRATING", "STATUS: UNKNOWN"]
    
    for _ in range(150):
        part = random.choice(catalog)["Part_ID"]
        status = random.choice(statuses)
        log_lines.append(f"[SYS_LOG] Timestamp: {random.randint(1600000000, 1700000000)} | Diagnostic check for {part} | Result: {status}")

    # Inject the targets amidst the noise
    log_lines.insert(23, "[SYS_LOG] Timestamp: 1698765432 | Diagnostic check for SUS-404 | Result: STATUS: CRITICAL_FRACTURE -- IMMEDIATE REPAIR REQUIRED")
    log_lines.insert(87, "WARNING: Inspection on component FRM-88X yielded STATUS: NEEDS_WELDING. Structural integrity compromised.")
    log_lines.insert(134, ">> ERROR: MNT-001 failure detected. STATUS: CRITICAL_FRACTURE. Do not operate vehicle.")
    
    # Add some more noise
    for _ in range(50):
        log_lines.append(f"DEBUG: Sensor ping {random.randint(100,999)} ms")

    with open(os.path.join(base_dir, "scanner_dump.txt"), "w") as f:
        f.write("\n".join(log_lines))

if __name__ == "__main__":
    build_env()
