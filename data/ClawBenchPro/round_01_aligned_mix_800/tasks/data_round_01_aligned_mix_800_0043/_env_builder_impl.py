import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("donations/batch_1", exist_ok=True)
    os.makedirs("pricing", exist_ok=True)
    
    parts_pricing = {
        "Apple": {"screen": 80, "battery": 40, "keyboard": 50},
        "Dell": {"screen": 45, "battery": 30, "keyboard": 25},
        "Lenovo": {"screen": 50, "battery": 35, "keyboard": 20}
    }
    with open("pricing/parts.json", "w") as f:
        json.dump(parts_pricing, f, indent=2)
        
    batch1_csv = [
        ["device_id", "brand", "model", "ram_gb", "storage_gb", "issues"],
        ["D101", "Apple", "Macbook", "8", "256", "cracked_screen|dead_battery"],
        ["D102", "Dell", "Latitude", "4", "256", "dead_battery"],
        ["D103", "Lenovo", "Thinkpad", "2", "128", "none"],
        ["D104", "Dell", "Inspiron", "8", "512", "water_damage"]
    ]
    with open("donations/batch_1/partA.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(batch1_csv)
        
    batch1_json = [
        {"id": "D105", "specs": {"brand": "Lenovo", "ram": 8}, "defects": ["cracked_screen", "keyboard"]},
        {"id": "D106", "specs": {"brand": "Apple", "ram": 4}, "defects": ["keyboard"]},
        {"id": "D107", "specs": {"brand": "Dell", "ram": 16}, "defects": ["cracked_screen"]},
        {"id": "D108", "specs": {"brand": "Lenovo", "ram": 8}, "defects": ["dead_battery", "keyboard"]}
    ]
    with open("donations/batch_1/partB.json", "w") as f:
        json.dump(batch1_json, f, indent=2)

def build_turn_2():
    os.makedirs("donations/batch_2", exist_ok=True)
    batch2_data = [
        {"id": "D201", "brand": "Apple", "ram": 16, "issues": ["dead_battery", "keyboard"]},
        {"id": "D202", "brand": "Dell", "ram": 8, "issues": ["dead_battery", "cracked_screen"]},
        {"id": "D203", "brand": "Lenovo", "ram": 16, "issues": ["cracked_screen", "dead_battery"]},
        {"id": "D204", "brand": "Apple", "ram": 4, "issues": ["water_damage"]},
        {"id": "D205", "brand": "Dell", "ram": 4, "issues": ["keyboard"]},
        {"id": "D206", "brand": "Lenovo", "ram": 8, "issues": ["keyboard"]},
        {"id": "D207", "brand": "Lenovo", "ram": 8, "issues": ["cracked_screen"]},
        {"id": "D208", "brand": "Dell", "ram": 8, "issues": ["cracked_screen"]}
    ]
    
    xml_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<devices>\n"
    for d in batch2_data:
        xml_content += f'  <device id="{d["id"]}">\n'
        xml_content += f'    <brand>{d["brand"]}</brand>\n'
        xml_content += f'    <ram>{d["ram"]}</ram>\n'
        xml_content += f'    <issues>{",".join(d["issues"])}</issues>\n'
        xml_content += f'  </device>\n'
    xml_content += "</devices>"
    
    with open("donations/batch_2/new_arrivals.xml", "w") as f:
        f.write(xml_content)

def build_turn_3():
    os.makedirs("supplier_updates", exist_ok=True)
    out_of_stock = [
        ["brand", "part"],
        ["Apple", "keyboard"],
        ["Dell", "battery"]
    ]
    with open("supplier_updates/out_of_stock.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(out_of_stock)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
