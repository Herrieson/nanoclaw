import os
import csv

def build_env():
    # Define the workspace directory
    workspace = os.path.join("assets", "data_265")
    os.makedirs(workspace, exist_ok=True)

    # 1. Create inventory_log.txt
    inventory_content = """
Inventory Update - Q3
=====================
Some of my personal vintage collections mixed with old hospital assets.

[1945] X-Ray Machine - SN: XR-45-A2 (Status: Archived, Location: Basement)
[2010] Defibrillator - SN: DF-10-B1 (Status: Active)
[1920] Antique Scalpel Set - SN: SS-20-C9 (Status: Archived, Location: Display Case A)
Note: We also have a [1965] Vintage Stethoscope - SN: VS-65-D4 but it's not old enough for the 1950s exhibit.
[1938] Iron Lung - SN: IL-38-E5 (Status: Archived, very heavy!)
[1980] Ultrasound - SN: US-80-F6 (Status: Scrapped)
[1890] Bloodletting Fleam - SN: BL-90-G7 (Status: Archived, pristine condition)
[1950] Glass Syringe Kit - SN: GS-50-H8 (Status: Archived)
[1951] Early Pacemaker - SN: PM-51-J9 (Status: Archived)
"""
    with open(os.path.join(workspace, "inventory_log.txt"), "w", encoding="utf-8") as f:
        f.write(inventory_content.strip())

    # 2. Create hospital_maintenance.csv
    csv_data = [
        ["Department", "Equipment", "Serial_Number", "Status", "Last_Checked"],
        ["Cardiology", "ECG", "ECG-112", "Working", "2023-10-01"],
        ["Internal Medicine", "Ultrasound", "US-224", "Working", "2023-09-15"],
        ["Internal Medicine", "MRI", "MRI-99X-BROKEN", "Needs Repair", "2023-10-20"],
        ["Emergency", "Defibrillator", "DF-88Y", "Working", "2023-10-21"],
        ["Pediatrics", "Incubator", "INC-55A", "Needs Repair", "2023-10-18"],
        ["Internal Medicine", "X-Ray", "XR-77Z", "Working", "2023-10-05"]
    ]
    with open(os.path.join(workspace, "hospital_maintenance.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
