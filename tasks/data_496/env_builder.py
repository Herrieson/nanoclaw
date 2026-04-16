import os
import random
import json
import string

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_environment():
    base_dir = "assets/data_496/estate_lot_logs"
    os.makedirs(base_dir, exist_ok=True)

    equipment_types = ["X-Ray Machine", "ECG Monitor", "Ventilator", "Defibrillator", "Surgical Table", "Centrifuge"]
    
    # Targets that MUST be found (Defibrillator, < 1990)
    targets = [
        {"type": "Defibrillator", "model": "LifePak-4", "year": 1985, "serial": "LP4-85-A102"},
        {"type": "Defibrillator", "model": "HeartStart-1", "year": 1989, "serial": "HS1-89-B991"},
        {"type": "Defibrillator", "model": "Zoll-PD", "year": 1978, "serial": "ZPD-78-C334"}
    ]

    # Decoys that MUST NOT be found
    decoys = [
        {"type": "Defibrillator", "model": "LifePak-9", "year": 1995, "serial": "LP9-95-D404"}, # Too new
        {"type": "Defibrillator", "model": "HeartStart-2", "year": 1990, "serial": "HS2-90-E505"}, # 1990 is not *before* 1990
        {"type": "ECG Monitor", "model": "Cardio-80", "year": 1982, "serial": "CM80-82-F606"}, # Wrong type
        {"type": "Defibrillator", "model": "Unknown-Pre", "year": 1980, "serial": None} # Missing serial, should be handled gracefully or ignored if serial is strictly required, but let's say it's just invalid data.
    ]

    items = targets + decoys

    # Add random noise items
    for _ in range(80):
        items.append({
            "type": random.choice(equipment_types),
            "model": f"Model-{generate_random_string(4)}",
            "year": random.randint(1960, 2010),
            "serial": generate_random_string(12)
        })

    random.shuffle(items)

    # Distribute into different file formats to simulate "messy logs"
    for i, item in enumerate(items):
        file_idx = i // 5
        format_type = random.choice(["json", "txt_kv", "xml", "log_messy"])
        filename = os.path.join(base_dir, f"inventory_batch_{file_idx}_{format_type}.txt")
        
        mode = 'a' if os.path.exists(filename) else 'w'
        with open(filename, mode) as f:
            if format_type == "json":
                f.write(json.dumps(item) + "\n")
            elif format_type == "txt_kv":
                f.write(f"---\nType: {item['type']}\nModel: {item['model']}\nYear: {item['year']}\nSerial Number: {item['serial']}\n---\n")
            elif format_type == "xml":
                f.write(f"<item><type>{item['type']}</type><model>{item['model']}</model><year>{item['year']}</year><serial>{item['serial']}</serial></item>\n")
            elif format_type == "log_messy":
                f.write(f"[INFO] 1999-12-31 Asset Scanned. Equipment Details => TYPE=[{item['type']}] MODEL=[{item['model']}] YR=[{item['year']}] SN=[{item['serial']}] Status=OK\n")

if __name__ == "__main__":
    create_environment()
