import os
import json
import csv

def build_env():
    base_dir = "assets/data_289"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. rates.json
    rates = {
        "Mercy General": 28.50,
        "St. Jude": 30.00,
        "Oak Creek Care": 26.00
    }
    with open(os.path.join(base_dir, "rates.json"), "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=4)
        
    # 2. paystubs.csv
    # Total paid: 1750.00
    paystubs = [
        ["Date", "Amount"],
        ["2023-10-06", "950.00"],
        ["2023-10-13", "800.00"]
    ]
    with open(os.path.join(base_dir, "paystubs.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(paystubs)
        
    # 3. shift_logs directory
    logs_dir = os.path.join(base_dir, "shift_logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Text format
    # Mercy: 24, Oak: 8
    with open(os.path.join(logs_dir, "week1_tracking.txt"), "w", encoding="utf-8") as f:
        f.write("Shift notes for week 1.\n")
        f.write("10/02: Worked at Mercy General for 12 hours. Tiring shift.\n")
        f.write("10/03: Oak Creek Care, 8 hours.\n")
        f.write("10/04: Mercy General, 12 hrs. Need more coffee.\n")
        
    # JSON format
    # St. Jude: 24
    json_log = [
        {"date": "10/09", "hospital": "St. Jude", "duration": 12},
        {"date": "10/10", "hospital": "St. Jude", "duration": 12}
    ]
    with open(os.path.join(logs_dir, "week2_export.json"), "w", encoding="utf-8") as f:
        json.dump(json_log, f, indent=4)
        
    # CSV format
    # Oak: 12, Mercy: 8
    csv_log = [
        ["Date", "Location", "Hours"],
        ["10/16", "Oak Creek Care", "12"],
        ["10/17", "Mercy General", "8"]
    ]
    with open(os.path.join(logs_dir, "week3_log.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_log)

if __name__ == "__main__":
    build_env()
