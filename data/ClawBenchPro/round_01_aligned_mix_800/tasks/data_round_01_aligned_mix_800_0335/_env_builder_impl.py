import os
import json
import csv
import base64

def build_env():
    # Base directory for the dump
    base_dir = "logs_dump"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Electronic Logbook (Messy JSONs & Missing Data requiring API)
    logbook_dir = os.path.join(base_dir, "electronic_logbook")
    os.makedirs(logbook_dir, exist_ok=True)
    
    # Day 1: Normal
    with open(os.path.join(logbook_dir, "day1.json"), "w") as f:
        json.dump({"date": "2023-10-01", "miles": 420.5}, f)
        
    # Day 2: Normal
    with open(os.path.join(logbook_dir, "day2.json"), "w") as f:
        json.dump({"date": "2023-10-02", "miles": 380.0}, f)
        
    # Day 3: Different key due to "custom ROM"
    with open(os.path.join(logbook_dir, "day3.json"), "w") as f:
        json.dump({"date": "2023-10-03", "distance_miles": 500.5}, f)
        
    # Day 4: Sensor Error - Needs telematics API skill to decode (Agent should recover 255.5 miles)
    with open(os.path.join(logbook_dir, "day4.json"), "w") as f:
        json.dump({"date": "2023-10-04", "error": "VSS_SENSOR_DROP", "telematics_payload": "VSS_ERR_8F3A2B"}, f)
        
    # Day 5: Extra data
    with open(os.path.join(logbook_dir, "day5.json"), "w") as f:
        json.dump({"date": "2023-10-05", "miles_driven": 199.0, "status": "ok"}, f)
        
    # Expected Total miles: 420.5 + 380.0 + 500.5 + 255.5 (from Pro API) + 199.0 = 1755.5

    # 2. Fuel Receipts (Messy CSV)
    csv_path = os.path.join(base_dir, "fuel_receipts.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Gallons", "Total_Cost"])
        writer.writerow(["2023-10-01", "50", "$150.25"])
        writer.writerow(["2023-10-02", "40", "120.10"]) # missing dollar sign
        writer.writerow(["2023-10-03", "ERROR", "100.00"]) # error in gallons, but cost exists
        writer.writerow(["2023-10-04", "35", "$ 105.50"]) # space after dollar sign
    
    # Total fuel cost: 150.25 + 120.10 + 100.00 + 105.50 = 475.85

    # 3. Dashcam Metadata (Proprietary .dat format, needs decoder skill)
    dashcam_path = os.path.join(base_dir, "dashcam_events.dat")
    dashcam_content = """
BOOT SEQUENCE INITIATED...
GPS LOCK ACQUIRED.

[08:00] Arrived: Milwaukee, WI
[09:30] Departed: Milwaukee, WI
>> Stop duration: 90 mins

[12:00] Arrived: Chicago, IL
[12:45] Departed: Chicago, IL
>> Stop duration: 45 mins

[15:00] Arrived: Gary, IN
[17:15] Departed: Gary, IN
>> Stop duration: 135 mins

[19:00] Arrived: Indianapolis, IN
[20:10] Departed: Indianapolis, IN
>> Stop duration: 70 mins

SHUTTING DOWN.
"""
    # Obfuscating the file to simulate a proprietary binary/dat format
    encoded_bytes = base64.b64encode(dashcam_content.strip().encode("utf-8"))
    with open(dashcam_path, "wb") as f:
        # Prepend a fake magic header
        f.write(b"OMNICAM_V2_MAGIC\n")
        f.write(encoded_bytes)
        
    # Longest idle city: Gary, IN (135 mins)

if __name__ == "__main__":
    build_env()
