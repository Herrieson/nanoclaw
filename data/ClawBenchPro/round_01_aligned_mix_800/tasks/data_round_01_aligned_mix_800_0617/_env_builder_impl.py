import os
import json
import csv

def build_env():
    # Create directories
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("specs", exist_ok=True)

    # Box 1 CSV (contains normal, 0, and negative stock)
    csv_path = os.path.join("inventory", "box1.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["part_name", "quantity"])
        writer.writerow(["chrome_wheels", "20"])
        writer.writerow(["chassis_frame", "0"])
        writer.writerow(["exhaust_pipe", "-2"])
        writer.writerow(["steering_wheel", "5"])

    # Box 2 JSON (contains integer and weird string stock)
    json_path = os.path.join("inventory", "box2.json")
    json_data = [
        {"name": "cab_roof", "qty": 1},
        {"name": "mud_flaps", "qty": 0},
        {"name": "front_grille", "qty": "none"},
        {"name": "headlights", "qty": 4}
    ]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)

    # Blueprints text (mixed units)
    txt_path = os.path.join("specs", "blueprints.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("--- Peterbilt 379 Scale Model Specs ---\n")
        f.write("Main Cab Body: 15.5 inch\n")
        f.write("Extended Trailer length: 50.8 cm\n")  # 50.8 / 2.54 = 20.0 inch
        f.write("Rear Axle width: 8.2 cm\n")           # 8.2 / 2.54 = 3.22 inch
        f.write("Chrome Smoke stack: 4.0 inch\n")

if __name__ == "__main__":
    build_env()
