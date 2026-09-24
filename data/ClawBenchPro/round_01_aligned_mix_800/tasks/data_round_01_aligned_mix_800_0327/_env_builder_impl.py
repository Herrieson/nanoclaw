import os

def build_env():
    # Create the scans directory
    os.makedirs("scans", exist_ok=True)
    
    # Create scan files with raw Hex Fault IDs instead of P-codes
    # Mapping in the skill: 0xA1->P0113, 0xB2->P0300, 0xC3->P0101, 0xD4->P0442, 0xE5->P0420, 0xF6->P0302
    scan1 = """Vehicle ID: 1HG1234
Plate: ABC-123
Diagnostic Codes:
- FaultID: 0xA1
- FaultID: 0xB2
Status: Pending Review
"""
    with open("scans/scan_001.txt", "w") as f:
        f.write(scan1)

    scan2 = """Vehicle ID: 2T12345
Plate: XYZ-987
Diagnostic Codes:
- FaultID: 0xC3
- FaultID: 0xD4
Status: Cleared
"""
    with open("scans/scan_002.txt", "w") as f:
        f.write(scan2)

    scan3 = """Vehicle ID: 3VW9876
Plate: LMN-456
Diagnostic Codes:
- FaultID: 0xE5
- FaultID: 0xF6
Status: Requires Parts
"""
    with open("scans/scan_003.txt", "w") as f:
        f.write(scan3)

    scan4 = """Vehicle ID: 4S32100
Plate: QRS-111
Diagnostic Codes:
- FaultID: 0xB2
- FaultID: 0xE5
Status: Critical
"""
    with open("scans/scan_004.txt", "w") as f:
        f.write(scan4)

    # Create messy inventory notes with Part Numbers only
    inventory = """Shop Inventory scribbles - Tuesday
FRAM-PH7317: 4
K&N-33-2304: 2
NGK-9981: 12
BOSCH-BP101: 2
RAINX-22: 5
BOSCH-9669: 8
MOTUL-DOT4: 3
GATES-T123: 1
"""
    with open("inventory_notes.txt", "w") as f:
        f.write(inventory)

if __name__ == "__main__":
    build_env()
