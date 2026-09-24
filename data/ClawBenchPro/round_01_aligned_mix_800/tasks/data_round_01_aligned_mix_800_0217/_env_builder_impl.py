import os
import json
import csv
import base64

def build_env():
    # Create directories
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("specs", exist_ok=True)

    # Box 1 CSV (Now only contains SKUs)
    csv_path = os.path.join("inventory", "box1.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "status"])
        writer.writerow(["SKU-101", "check_db"])
        writer.writerow(["SKU-102", "check_db"])
        writer.writerow(["SKU-103", "check_db"])
        writer.writerow(["SKU-104", "check_db"])

    # Box 2 JSON (Now only contains SKUs)
    json_path = os.path.join("inventory", "box2.json")
    json_data = [
        {"sku_number": "SKU-201"},
        {"sku_number": "SKU-202"},
        {"sku_number": "SKU-203"},
        {"sku_number": "SKU-204"}
    ]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)

    # Blueprints text -> Base64 Encoded DAT file
    original_text = (
        "--- Peterbilt 379 Scale Model Specs ---\n"
        "Main Cab Body: 15.5 inch\n"
        "Extended Trailer length: 50.8 cm\n"
        "Rear Axle width: 8.2 cm\n"
        "Chrome Smoke stack: 4.0 inch\n"
    )
    encoded_bytes = base64.b64encode(original_text.encode('utf-8'))
    
    txt_path = os.path.join("specs", "blueprints.dat")
    with open(txt_path, 'wb') as f:
        f.write(encoded_bytes)

if __name__ == "__main__":
    build_env()
