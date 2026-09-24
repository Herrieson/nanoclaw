import os
import json
import random
import uuid
from datetime import datetime, timedelta

def build_env():
    base_dir = "logs_dump"
    os.makedirs(base_dir, exist_ok=True)
    
    # ---------------------------------------------------------
    # 1. Generate Mileage Data (OBD2 Telemetry)
    # ---------------------------------------------------------
    obd2_dir = os.path.join(base_dir, "obd2_telemetry")
    os.makedirs(obd2_dir, exist_ok=True)
    
    firmwares = ["v1.0-stable", "v2.0-alpha", "v2.3.9", "v2.4.0-rc", "v2.4.1-beta"]
    valid_miles = [350.5, 410.2, 195.3, 500.0, 220.8, 330.1, 405.6, 290.4, 310.7, 450.9]
    # Total valid miles will be exactly 3464.5
    
    valid_mile_idx = 0
    for month in range(1, 13):
        for day in range(1, 29):
            date_str = f"2023-{month:02d}-{day:02d}"
            daily_dir = os.path.join(obd2_dir, f"2023", f"{month:02d}", f"{day:02d}")
            os.makedirs(daily_dir, exist_ok=True)
            
            # Decide if we put a valid log here
            if valid_mile_idx < len(valid_miles) and random.random() > 0.85:
                fw = "v2.4.1-beta"
                miles = valid_miles[valid_mile_idx]
                valid_mile_idx += 1
            else:
                fw = random.choice([f for f in firmwares if f != "v2.4.1-beta"])
                miles = round(random.uniform(50.0, 600.0), 1)
            
            # Randomize the key for distance
            dist_key = random.choice(["miles", "distance", "dist_mi", "distance_driven"])
            
            log_data = {
                "timestamp": f"{date_str}T23:59:59Z",
                "device_id": f"ESP32-{uuid.uuid4().hex[:6]}",
                "firmware_version": fw,
                "diagnostics": {
                    "engine_status": "OK",
                    "oil_pressure": random.randint(30, 60),
                    dist_key: miles if fw == "v2.4.1-beta" else "ERR_SENSOR_NO_DATA" if random.random() > 0.5 else miles
                }
            }
            
            # Also generate some corrupted/noise files
            for _ in range(random.randint(1, 3)):
                noise_name = f"chunk_{uuid.uuid4().hex[:8]}.json"
                with open(os.path.join(daily_dir, noise_name), "w") as f:
                    if random.random() > 0.2:
                        json.dump(log_data, f, indent=2)
                    else:
                        f.write("{corrupted_json: true, ") # deliberate syntax error
    
    # ---------------------------------------------------------
    # 2. Generate Fuel Receipts (OCR Scans)
    # ---------------------------------------------------------
    ocr_dir = os.path.join(base_dir, "ocr_receipts")
    os.makedirs(ocr_dir, exist_ok=True)
    
    valid_fuel_amounts = [150.25, 85.50, 210.75, 45.00, 120.00, 95.50, 300.25, 65.50, 110.00, 134.50]
    # Total valid fuel will be exactly 1317.25
    
    valid_fuel_idx = 0
    for i in range(300):
        file_path = os.path.join(ocr_dir, f"scan_{uuid.uuid4().hex[:12]}.txt")
        
        if valid_fuel_idx < len(valid_fuel_amounts) and random.random() > 0.8:
            amount = valid_fuel_amounts[valid_fuel_idx]
            valid_fuel_idx += 1
            content = f"TAG: PRJ-FUEL-99\n"
            content += f"STATION: {random.choice(['Pilot', 'Loves', 'Flying J', 'BP'])}\n"
            content += "MERCHANT COPY\n"
            
            # Messy formatting variants for the regex challenge
            formats = [
                f"Cost: $ {amount}",
                f"Total Amount: {amount} USD",
                f"TOTAL.....${amount}",
                f"Amount Due: {amount}",
                f"Total Cost :$ {amount}"
            ]
            content += f"{random.choice(formats)}\n"
            content += "THANK YOU COME AGAIN"
        else:
            # Decoy receipts (menus, groceries, toll booths - NO valid tag)
            if random.random() > 0.5:
                content = "TAG: GROCERY-01\nWALMART SUPERCENTER\nMilk: 4.99\nBread: 2.50\nTotal Amount: 7.49 USD"
            else:
                content = f"JOES DINER\nCheeseburger: 12.00\nCoffee: 3.50\nTOTAL.....$15.50\nTip: 3.00"
                if random.random() > 0.8:
                    content = "TAG: PRJ-PARTS-99\n" + content # Close but wrong tag
        
        with open(file_path, "w") as f:
            f.write(content)
            
    # ---------------------------------------------------------
    # 3. Generate Dashcam GPS & Geo Map
    # ---------------------------------------------------------
    dashcam_dir = os.path.join(base_dir, "dashcam_gps")
    os.makedirs(dashcam_dir, exist_ok=True)
    
    geo_map = {
        "43.0389,-87.9065": "Milwaukee, WI",
        "41.8781,-87.6298": "Chicago, IL",
        "41.5934,-87.3464": "Gary, IN",
        "39.7684,-86.1581": "Indianapolis, IN",
        "38.6270,-90.1994": "St. Louis, MO"
    }
    
    ref_dir = os.path.join(base_dir, "reference")
    os.makedirs(ref_dir, exist_ok=True)
    with open(os.path.join(ref_dir, "geo_map.json"), "w") as f:
        json.dump(geo_map, f, indent=4)
        
    start_time = datetime(2023, 1, 1, 8, 0, 0)
    
    # We will generate logs for 50 days. 
    # Gary, IN will have the absolute longest idle (6 hours).
    # Other cities will have stops between 1 and 4 hours.
    
    for day in range(50):
        current_time = start_time + timedelta(days=day)
        log_content = f"--- BOOT SEQ {day} ---\n"
        
        num_stops = random.randint(1, 4)
        for stop in range(num_stops):
            loc = random.choice(list(geo_map.keys()))
            
            # Plant the definitive longest stop
            if day == 25 and stop == 0:
                loc = "41.5934,-87.3464" # Gary, IN
                duration = timedelta(hours=6, minutes=15)
            else:
                duration = timedelta(hours=random.randint(1, 3), minutes=random.randint(0, 59))
                
            log_content += f"[{current_time.isoformat()}] EVENT: IDLE_START | LOC: {loc}\n"
            current_time += duration
            log_content += f"[{current_time.isoformat()}] EVENT: MOVING | LOC: {loc}\n"
            current_time += timedelta(hours=random.randint(1, 4)) # driving time
            
        with open(os.path.join(dashcam_dir, f"gps_track_{day:03d}.log"), "w") as f:
            f.write(log_content)

if __name__ == "__main__":
    build_env()
