import os
import json
import random

def build_env():
    base_dir = "assets/data_462"
    os.makedirs(base_dir, exist_ok=True)

    tenants = {
        "101": {"name": "Alice Smith", "lease": "1yr"},
        "102": {"name": "Bob Johnson", "lease": "month-to-month"},
        "103": {"name": "Charlie Brown", "lease": "2yr"},
        "201": {"name": "Diana Prince", "lease": "1yr"},
        "202": {"name": "Eve Adams", "lease": "1yr"},
        "203": {"name": "Frank Castle", "lease": "month-to-month"},
        "301": {"name": "Grace Hopper", "lease": "1yr"},
        "302": {"name": "Hank Pym", "lease": "1yr"},
        "303": {"name": "Ivy Pepper", "lease": "month-to-month"}
    }

    with open(os.path.join(base_dir, "tenants.json"), "w") as f:
        json.dump(tenants, f, indent=4)

    # We will rig units 203, 301, and 102 to be the top 3 offenders.
    # Target totals:
    # 203: ~4500
    # 301: ~4200
    # 102: ~3900
    # Others: ~1500 - 2500

    log_entries = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for month in months:
        for unit in tenants.keys():
            if unit == "203":
                w = random.randint(100, 150)
                e = random.randint(200, 250)
            elif unit == "301":
                w = random.randint(90, 140)
                e = random.randint(180, 240)
            elif unit == "102":
                w = random.randint(80, 120)
                e = random.randint(170, 220)
            else:
                w = random.randint(30, 70)
                e = random.randint(80, 130)
            
            # Mix up the formatting to make parsing slightly challenging
            fmt_type = random.choice([1, 2, 3])
            if fmt_type == 1:
                log_entries.append(f"Month: {month} | Unit: {unit} | Water: {w} | Elec: {e}")
            elif fmt_type == 2:
                log_entries.append(f"{month} - UNIT {unit} - W:{w} E:{e}")
            else:
                log_entries.append(f"Record [{month}] unit={unit};water={w};electricity={e}")

    random.shuffle(log_entries)
    
    # Inject some noise
    log_entries.insert(10, "ERROR: Meter connection failed for unit 999")
    log_entries.insert(45, "Note: Checked 202's AC unit on Mar 15.")

    with open(os.path.join(base_dir, "utility_log.txt"), "w") as f:
        for entry in log_entries:
            f.write(entry + "\n")

if __name__ == "__main__":
    build_env()
