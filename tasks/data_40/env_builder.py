import os
import json

def build_env():
    base_dir = "assets/data_40"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Gas Station Logs
    logs_dir = os.path.join(base_dir, "gas_station_logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    log1_content = """08:00|Regular|10.0|3.50
09:15|Premium|20.5|4.20
SYSTEM_REBOOT_ERROR|MEMORY_FAULT
10:30|Premium|15.0|4.20
11:00|Diesel|30.0|4.10"""

    log2_content = """13:00|Regular|25.0|3.50
14:00|Diesel|50.0|4.50
16:45|Premium|40.0|4.20
PRINTER_OUT_OF_PAPER"""

    with open(os.path.join(logs_dir, "shift_20231001.log"), "w") as f:
        f.write(log1_content)
        
    with open(os.path.join(logs_dir, "shift_20231002.log"), "w") as f:
        f.write(log2_content)
        
    # 2. Deliveries JSON
    deliveries = [
        {"date": "2023-10-01", "grade": "Premium", "gallons_delivered": 100.0},
        {"date": "2023-10-02", "grade": "Regular", "gallons_delivered": 500.0},
        {"date": "2023-10-02", "grade": "Diesel", "gallons_delivered": 200.0}
    ]
    with open(os.path.join(base_dir, "deliveries.json"), "w") as f:
        json.dump(deliveries, f, indent=2)
        
    # 3. Deck Receipts
    deck_text = """Went to the hardware store after dropping the kids off. 
Lumber was $250.75. 
Screws cost $15.50. 
I also bought a new drill for $89.99 because the old one broke.
Grabbed a soda for $1.50 on the way out."""
    
    with open(os.path.join(base_dir, "deck_receipts.txt"), "w") as f:
        f.write(deck_text)

if __name__ == "__main__":
    build_env()
