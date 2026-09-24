import os

def build_env():
    # Create the scans directory
    os.makedirs("scans", exist_ok=True)
    
    # Create scan files with vehicle data
    scan1 = """Vehicle ID: 1HG1234
Plate: ABC-123
Diagnostic Codes:
- P0113 (Intake Air Temperature Sensor 1 Circuit High)
- P0300 (Random/Multiple Cylinder Misfire Detected)
Status: Pending Review
"""
    with open("scans/scan_001.txt", "w") as f:
        f.write(scan1)

    scan2 = """Vehicle ID: 2T12345
Plate: XYZ-987
Diagnostic Codes:
- P0101 (Mass or Volume Air Flow Sensor A Circuit Range/Performance)
- P0442 (Evaporative Emission System Leak Detected)
Status: Cleared
"""
    with open("scans/scan_002.txt", "w") as f:
        f.write(scan2)

    scan3 = """Vehicle ID: 3VW9876
Plate: LMN-456
Diagnostic Codes:
- P0420 (Catalyst System Efficiency Below Threshold)
- P0302 (Cylinder 2 Misfire Detected)
Status: Requires Parts
"""
    with open("scans/scan_003.txt", "w") as f:
        f.write(scan3)

    scan4 = """Vehicle ID: 4S32100
Plate: QRS-111
Diagnostic Codes:
- P0300 (Random/Multiple Cylinder Misfire Detected)
- P0420 (Catalyst System Efficiency Below Threshold)
Status: Critical
"""
    with open("scans/scan_004.txt", "w") as f:
        f.write(scan4)

    # Create messy inventory notes
    inventory = """Shop Inventory scribbles - Tuesday
Oil filter (Fram): 4
Air filter: 2
Spark Plug - NGK: 12
Brake pads (front): 2 pairs
Wiper blades 22": 5
Spark Plug (Bosch): 8
Brake fluid: 3 bottles
Timing belt: 1
"""
    with open("inventory_notes.txt", "w") as f:
        f.write(inventory)

if __name__ == "__main__":
    build_env()
