import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 1. Create directory structure
    os.makedirs("dispatch/active_cases", exist_ok=True)
    os.makedirs("dispatch/camera_logs", exist_ok=True)
    os.makedirs("dispatch/sys_config", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    random.seed(42)

    # 2. Build the System Config (Camera Registry)
    cameras = {
        "CAM_01": "Elm Street Crossing",
        "CAM_02": "Downtown Avenue",
        "CAM_03": "Mile Marker 42",
        "CAM_04": "Main St Junction",
        "CAM_05": "Route 66 Bridge",
        "CAM_06": "Industrial Park Blvd",
        "CAM_07": "Valley Highway Exit",
        "CAM_08": "Sunset Boulevard",
        "CAM_09": "Pine Ridge Road",
        "CAM_10": "Airport Expressway"
    }
    with open("dispatch/sys_config/camera_registry.json", "w") as f:
        json.dump({
            "system_version": "2.4.1",
            "last_updated": "2023-01-15",
            "sensors": [{"id": k, "location_name": v, "operational": True} for k, v in cameras.items()]
        }, f, indent=4)

    # 3. Build Active Cases (Massive fragmentation & noise)
    # Target plates:
    # "NVR-0012" -> STOLEN (Spotted today)
    # "BKL-1002" -> WANTED (Spotted today)
    # "FAL-9921" -> RECOVERED (Spotted today, should NOT be reported)
    # "GLX-8443" -> STOLEN (Spotted yesterday, should NOT be reported)
    target_plates = [
        {"plate": "NVR-0012", "status": "STOLEN"},
        {"plate": "BKL-1002", "status": "WANTED"},
        {"plate": "FAL-9921", "status": "RECOVERED"},
        {"plate": "GLX-8443", "status": "STOLEN"},
    ]
    
    precincts = ["north_side", "south_side", "east_end", "west_valley"]
    for p in precincts:
        os.makedirs(f"dispatch/active_cases/{p}/2023", exist_ok=True)
        # Generate 50 junk case files per precinct
        for i in range(50):
            plate = f"{chr(random.randint(65,90))}{chr(random.randint(65,90))}{chr(random.randint(65,90))}-{random.randint(1000,9999)}"
            status = random.choice(["CLOSED", "RECOVERED", "PENDING_REVIEW", "STOLEN"])
            file_type = random.choice(["json", "txt"])
            
            filepath = f"dispatch/active_cases/{p}/2023/case_{random.randint(10000,99999)}.{file_type}"
            if file_type == "json":
                with open(filepath, "w") as f:
                    json.dump({"vehicle_plate": plate, "case_status": status, "reported_by": "Officer"}, f)
            else:
                with open(filepath, "w") as f:
                    f.write(f"--- CASE FILE ---\nPLATE: {plate}\nSTATUS: {status}\n")
                    
    # Inject target cases
    with open("dispatch/active_cases/north_side/2023/case_99991.json", "w") as f:
        json.dump({"vehicle_plate": "NVR-0012", "case_status": "STOLEN", "owner": "John Doe"}, f)
    with open("dispatch/active_cases/east_end/2023/case_99992.txt", "w") as f:
        f.write("--- CASE FILE ---\nPLATE: BKL-1002\nSTATUS: WANTED\nCRIME: ARMED ROBBERY\n")
    with open("dispatch/active_cases/south_side/2023/case_99993.json", "w") as f:
        json.dump({"vehicle_plate": "FAL-9921", "case_status": "RECOVERED", "recovered_date": "2023-10-20"}, f)
    with open("dispatch/active_cases/west_valley/2023/case_99994.txt", "w") as f:
        f.write("--- CASE FILE ---\nPLATE: GLX-8443\nSTATUS: STOLEN\n")

    # 4. Build Camera Logs (Scale & Noise)
    start_date = datetime(2023, 10, 18)
    for day_offset in range(7): # Oct 18 to Oct 24
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        log_dir = f"dispatch/camera_logs/{date_str}"
        os.makedirs(log_dir, exist_ok=True)
        
        # 10 chunks per day
        for chunk in range(10):
            logs = []
            for _ in range(80): # 80 logs per chunk
                cam = random.choice(list(cameras.keys()))
                plate = f"{chr(random.randint(65,90))}{chr(random.randint(65,90))}{chr(random.randint(65,90))}-{random.randint(1000,9999)}"
                speed = random.randint(35, 80)
                stat = "NORMAL" if random.random() > 0.1 else random.choice(["TEST", "MAINTENANCE"])
                
                # Make CAM_02 look like a hotspot, but it's all TEST data
                if cam == "CAM_02" and random.random() > 0.5:
                    speed = random.randint(70, 120)
                    stat = "TEST"
                    
                log_line = f"EVT_ID:{random.randint(100000,999999)} || TS:{date_str} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d} || SENSOR:{cam} || READ:[LCP: {plate}] || VELOCITY: {speed}mph || STAT: {stat}"
                logs.append(log_line)
                
            # If it's today (Oct 24), inject specific behaviors
            if date_str == "2023-10-24" and chunk == 5:
                # CAM_07 is the REAL worst hotspot (Valley Highway Exit)
                for _ in range(45):
                    logs.append(f"EVT_ID:888888 || TS:{date_str} 14:00:00 || SENSOR:CAM_07 || READ:[LCP: RND-{random.randint(1000,9999)}] || VELOCITY: {random.randint(66, 95)}mph || STAT: NORMAL")
                # CAM_03 is a decoy hotspot (Mile Marker 42)
                for _ in range(25):
                    logs.append(f"EVT_ID:777777 || TS:{date_str} 15:00:00 || SENSOR:CAM_03 || READ:[LCP: RND-{random.randint(1000,9999)}] || VELOCITY: {random.randint(66, 85)}mph || STAT: NORMAL")
                
                # Inject target spotted plates
                logs.append(f"EVT_ID:111111 || TS:{date_str} 08:15:00 || SENSOR:CAM_04 || READ:[LCP: NVR-0012] || VELOCITY: 45mph || STAT: NORMAL")
                logs.append(f"EVT_ID:222222 || TS:{date_str} 09:30:00 || SENSOR:CAM_01 || READ:[LCP: BKL-1002] || VELOCITY: 55mph || STAT: NORMAL")
                logs.append(f"EVT_ID:333333 || TS:{date_str} 10:45:00 || SENSOR:CAM_09 || READ:[LCP: FAL-9921] || VELOCITY: 40mph || STAT: NORMAL") # Recovered
                
            if date_str == "2023-10-23" and chunk == 2:
                # GLX-8443 spotted yesterday
                logs.append(f"EVT_ID:444444 || TS:{date_str} 18:20:00 || SENSOR:CAM_06 || READ:[LCP: GLX-8443] || VELOCITY: 50mph || STAT: NORMAL")

            with open(f"{log_dir}/chunk_{chunk}.log", "w") as f:
                f.write("\n".join(logs))

if __name__ == "__main__":
    build_env()
