import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Set random seed for deterministic environment generation
    random.seed(1200)

    # 1. Create directories
    dirs = ["warehouse_sync", "system_configs", "hr_logs", "reports"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. System Config for Category Mapping
    category_map = {
        "categories": [
            {"code": "APR", "name": "Apparel", "valid_for_floor": True},
            {"code": "AUT", "name": "Automotive", "valid_for_floor": False},
            {"code": "HDW", "name": "Hardware", "valid_for_floor": False},
            {"code": "GRO", "name": "Grocery", "valid_for_floor": False},
            {"code": "FSH", "name": "Apparel", "valid_for_floor": True}, # Fashion is also apparel
            {"code": "HOM", "name": "Home Goods", "valid_for_floor": False}
        ]
    }
    # Hide it a bit deep with some noise files
    os.makedirs("system_configs/v2_legacy", exist_ok=True)
    with open("system_configs/v2_legacy/deprecated_map.json", "w") as f:
        json.dump({"APR": "Apple", "AUT": "Autumn"}, f)
    with open("system_configs/master_cat_codes.json", "w") as f:
        json.dump(category_map, f, indent=2)

    # 3. Generate Inventory Pallet Files
    # Store 42 is our target. Store 99 is noise.
    # Mix of CSV and JSON formats.
    sku_counter = 1000
    for pallet_id in range(1, 201):
        store_id = "042" if random.random() > 0.4 else "099"
        file_ext = "csv" if random.random() > 0.5 else "json"
        filename = f"warehouse_sync/pallet_{pallet_id:03d}_STORE-{store_id}.{file_ext}"
        
        items = []
        for _ in range(random.randint(5, 15)):
            cat = random.choice(["APR", "AUT", "HDW", "GRO", "FSH", "HOM"])
            sku = f"{cat}-{sku_counter}"
            sku_counter += 1
            qty = random.randint(1, 20)
            price = round(random.uniform(5.0, 55.0), 2)
            
            items.append({
                "SKU": sku,
                "Quantity": qty,
                "Unit_Price": price
            })
            
        if file_ext == "json":
            with open(filename, "w") as f:
                json.dump({"pallet_data": items}, f, indent=2)
        else:
            with open(filename, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["SKU", "Quantity", "Unit_Price"])
                for item in items:
                    writer.writerow([item["SKU"], item["Quantity"], item["Unit_Price"]])

    # 4. Generate HR Logs
    # Relevant dates: 2024-04-13 and 2024-04-14
    # Noise dates: 2024-04-10 to 2024-04-12
    employees = ["Sarah", "Mike", "Jessica", "David", "Emily", "Tom", "Alex", "Jordan"]
    
    # Pre-define their weekend working hours logic to ensure deterministic result
    # Overtime threshold: > 8.0 hours
    # Let's make Mike, Emily, and Jordan go overtime.
    
    def generate_day_log(date_str, shifts):
        lines = []
        for emp, periods in shifts.items():
            for p in periods:
                in_time, out_time = p
                lines.append(f"[{date_str} {in_time}:00] [EMP: {emp}] [EVENT: CLOCK_IN]")
                lines.append(f"[{date_str} {out_time}:00] [EMP: {emp}] [EVENT: CLOCK_OUT]")
        # Shuffle lines but keep IN before OUT? No, just sort by time to simulate a real log
        lines.sort()
        with open(f"hr_logs/timepunch_{date_str}.log", "w") as f:
            f.write("\n".join(lines) + "\n")

    # April 10 (Noise)
    generate_day_log("2024-04-10", {
        "Sarah": [("09:00", "17:00")], "Mike": [("08:00", "20:00")] # Overtime here shouldn't count for weekend
    })
    # April 11 (Noise)
    generate_day_log("2024-04-11", {
        "Jessica": [("10:00", "14:00")]
    })
    
    # April 13 (Weekend Day 1)
    generate_day_log("2024-04-13", {
        "Sarah": [("08:00", "12:00")],        # 4 hours
        "Mike": [("09:00", "14:00")],         # 5 hours
        "Jessica": [("10:00", "15:00")],      # 5 hours
        "Emily": [("08:00", "17:30")],        # 9.5 hours -> OVERTIME already
        "Jordan": [("12:00", "16:00")]        # 4 hours
    })

    # April 14 (Weekend Day 2)
    generate_day_log("2024-04-14", {
        "Sarah": [("13:00", "16:30")],        # 3.5 hours (Total: 7.5 - OK)
        "Mike": [("10:00", "14:00")],         # 4 hours (Total: 9.0 - OVERTIME)
        "David": [("09:00", "15:00")],        # 6 hours (Total: 6.0 - OK)
        "Jordan": [("09:00", "11:00"), ("12:00", "15:15")], # 2 + 3.25 = 5.25 (Total: 9.25 - OVERTIME)
        "Alex": [("16:00", "20:00")]          # 4 hours (Total: 4.0 - OK)
    })
    
    # Generate some corrupted noise lines in the logs just to enforce robust parsing
    with open("hr_logs/timepunch_2024-04-13.log", "a") as f:
        f.write("[2024-04-13 23:59:59] [SYSTEM] [EVENT: REBOOT_SEQUENCE_INITIATED]\n")
        f.write("ERROR: DATABASE CONNECTION LOST\n")

if __name__ == "__main__":
    build_env()
