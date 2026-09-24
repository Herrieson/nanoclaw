import os
import json
import csv
import random

def build_env():
    random.seed(42) # Ensure reproducible chaos
    
    os.makedirs("facility_logs", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    items = ["Bleach", "Soap", "Detergent", "Floor_Cleaner", "Bleach_Diluted", "Towels"]
    wings = ["North_Wing", "South_Wing", "East_Wing", "West_Wing"]
    rooms_pool = [f"{wing[0]}-{random.randint(100, 399)}" for wing in wings for _ in range(5)]
    missing_indicators = ["", "N/A", "None", "Unknown"]

    # Ground Truth Trackers
    gt_total_bleach_used = 0
    gt_total_bleach_lost = 0

    # 1. Generate logs
    for day in range(1, 32):
        date_str = f"2023-12-{day:02d}"
        for wing in wings:
            # Create valid and archive dirs
            valid_dir = os.path.join("facility_logs", wing, date_str)
            archive_dir = os.path.join("facility_logs", wing, "archive", date_str)
            os.makedirs(valid_dir, exist_ok=True)
            os.makedirs(archive_dir, exist_ok=True)

            # Generate files for each day/wing
            file_types = ["csv", "json", "txt"]
            for ftype in file_types:
                records = []
                for _ in range(random.randint(2, 6)):
                    item = random.choice(items)
                    qty = random.randint(1, 5)
                    
                    is_missing = random.random() < 0.2
                    room = random.choice(missing_indicators) if is_missing else random.choice(rooms_pool)

                    records.append({"item": item, "qty": qty, "room": room})

                # Write Valid File
                filename = f"shift_log_{random.randint(1000,9999)}.{ftype}"
                valid_path = os.path.join(valid_dir, filename)
                
                # Write Noise File (.bak or in archive)
                noise_path = os.path.join(archive_dir, f"backup_{filename}")
                noise_bak_path = os.path.join(valid_dir, f"{filename}.bak")
                
                for path in [valid_path, noise_path, noise_bak_path]:
                    is_valid = (path == valid_path)
                    
                    if ftype == "csv":
                        with open(path, "w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(["Item", "Quantity", "Room"])
                            for r in records:
                                writer.writerow([r["item"], r["qty"], r["room"]])
                                if is_valid and r["item"] == "Bleach":
                                    gt_total_bleach_used += r["qty"]
                                    if r["room"] in missing_indicators:
                                        gt_total_bleach_lost += r["qty"]

                    elif ftype == "json":
                        json_data = []
                        for r in records:
                            # Randomize json missing key a bit
                            j_record = {"item": r["item"], "amount": r["qty"]}
                            if r["room"] != "":
                                j_record["room_no"] = r["room"]
                            else:
                                j_record["room_no"] = None # JSON null
                            json_data.append(j_record)
                            
                            if is_valid and r["item"] == "Bleach":
                                gt_total_bleach_used += r["qty"]
                                if r["room"] in missing_indicators or r["room"] == "":
                                    gt_total_bleach_lost += r["qty"]
                                    
                        with open(path, "w") as f:
                            json.dump(json_data, f)

                    elif ftype == "txt":
                        with open(path, "w") as f:
                            for r in records:
                                f.write(f"Item: {r['item']} | Qty: {r['qty']} | Room: {r['room']}\n")
                                if is_valid and r["item"] == "Bleach":
                                    gt_total_bleach_used += r["qty"]
                                    if r["room"] in missing_indicators:
                                        gt_total_bleach_lost += r["qty"]

    # 2. Generate Inventory
    start_stock = 1500
    # Simulate realistic discrepancy
    # Suppose actual used is slightly more than log used (meaning items were stolen)
    actual_used = gt_total_bleach_used + random.randint(30, 80) 
    end_stock = start_stock - actual_used
    
    gt_discrepancy = gt_total_bleach_used - (start_stock - end_stock)

    stock_nov = {"Bleach": start_stock, "Soap": 3000, "Detergent": 1200}
    stock_dec = {"Bleach": end_stock, "Soap": 2700, "Detergent": 1050}

    with open("inventory/stock_Nov_30.json", "w") as f:
        json.dump(stock_nov, f)
    with open("inventory/stock_Dec_31.json", "w") as f:
        json.dump(stock_dec, f)

    # Save Ground Truth for evaluation platform reference (Hidden from Agent)
    # with open("reports/.gt.json", "w") as f:
    #     json.dump({
    #         "total_bleach_used": gt_total_bleach_used,
    #         "total_bleach_lost_in_logs": gt_total_bleach_lost,
    #         "inventory_discrepancy": gt_discrepancy
    #     }, f)

if __name__ == "__main__":
    build_env()
