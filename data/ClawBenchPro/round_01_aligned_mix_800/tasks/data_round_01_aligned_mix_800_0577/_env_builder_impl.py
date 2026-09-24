import os
import json
import random
import datetime

def build_env():
    os.makedirs("archives/vendors", exist_ok=True)
    os.makedirs("logs/gate_syslog", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    cuisines = ["American", "Thai", "Native American", "Italian", "Korean", "Mexican", "Japanese", "Indian", "Greek"]
    statuses = ["approved", "pending", "rejected", "revoked"]
    
    approved_valid_vendors = []
    
    # 1. Generate fragmented Vendor JSONs
    for i in range(1, 451):
        vendor_id = f"VND-{i:04d}"
        plate = f"{random.choice(['MT', 'WA', 'NM', 'NY', 'CA', 'OR', 'NJ', 'TX', 'AZ'])}-{random.randint(1000, 9999)}"
        cuisine = random.choice(cuisines)
        status = random.choices(statuses, weights=[0.4, 0.3, 0.2, 0.1])[0]
        
        # Decide validity date
        if random.random() > 0.3:
            # Valid date
            valid_until = "2024-10-27" if random.random() > 0.5 else f"2024-11-{random.randint(10, 30)}"
        else:
            # Expired date
            valid_until = f"2024-0{random.randint(1, 9)}-{random.randint(10, 28)}"
            
        vendor_data = {
            "vendor_id": vendor_id,
            "vendor_name": f"Food Truck {i}",
            "license_plate": plate,
            "cuisine_type": cuisine,
            "status": status,
            "valid_until": valid_until
        }
        
        if status == "approved" and vendor_data["valid_until"] >= "2024-10-27":
            approved_valid_vendors.append(plate)
            
        with open(f"archives/vendors/vendor_{vendor_id}.json", "w") as f:
            json.dump(vendor_data, f, indent=2)

    # 2. Generate Noisy Gate Syslogs
    gates = ["North", "South", "East"]
    dates = ["2024-10-24", "2024-10-25", "2024-10-26", "2024-10-27"]
    
    for date in dates:
        for gate in gates:
            log_filename = f"logs/gate_syslog/gate_{gate.lower()}_{date}.log"
            with open(log_filename, "w") as f:
                # Generate hundreds of noisy lines
                for _ in range(random.randint(200, 500)):
                    time_str = f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                    
                    event_type = random.choice(["ENTRY", "EXIT", "ERROR_READ", "HEARTBEAT", "SHIFT_CHANGE"])
                    if event_type == "HEARTBEAT":
                        f.write(f"[{date} {time_str}] [INFO] Gate={gate} System Check OK\n")
                    elif event_type == "ERROR_READ":
                        f.write(f"[{date} {time_str}] [WARN] Gate={gate} Action=ALPR_READ Error: Plate obstructed\n")
                    elif event_type == "SHIFT_CHANGE":
                        f.write(f"[{date} {time_str}] [INFO] Gate={gate} Action=SHIFT_CHANGE Operator changed\n")
                    else:
                        # ENTRY or EXIT
                        # Mix of approved and completely random plates
                        if random.random() > 0.4 and approved_valid_vendors:
                            plate = random.choice(approved_valid_vendors)
                        else:
                            # Unauthorized or random plates
                            plate = f"UNAUTH-{random.randint(100, 999)}"
                            
                        f.write(f"[{date} {time_str}] [INFO] Gate={gate} Action={event_type} Plate={plate} Weight={random.randint(2000, 6000)}kg\n")

if __name__ == "__main__":
    build_env()
