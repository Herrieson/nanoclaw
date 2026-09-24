import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 构建报名者名单，包含陷阱数据（例如 11岁+Nut-Free，必须放在低风险且全员Nut-Free的营地）
    campers = [
        {"ID": "C01", "Name": "Liam", "Age": 15, "Medical": "None", "Diet": "Standard"},
        {"ID": "C02", "Name": "Noah", "Age": 11, "Medical": "Asthma", "Diet": "Nut-Free"},
        {"ID": "C03", "Name": "Oliver", "Age": 14, "Medical": "None", "Diet": "Standard"},
        {"ID": "C04", "Name": "Elijah", "Age": 10, "Medical": "None", "Diet": "Standard"},
        {"ID": "C05", "Name": "James", "Age": 12, "Medical": "Bee Allergy", "Diet": "Standard"},
        {"ID": "C06", "Name": "William", "Age": 13, "Medical": "None", "Diet": "Nut-Free"},
        {"ID": "C07", "Name": "Benjamin", "Age": 11, "Medical": "None", "Diet": "Nut-Free"},
        {"ID": "C08", "Name": "Lucas", "Age": 16, "Medical": "None", "Diet": "Standard"},
        {"ID": "C09", "Name": "Henry", "Age": 17, "Medical": "None", "Diet": "Standard"},
        {"ID": "C10", "Name": "Theodore", "Age": 9, "Medical": "None", "Diet": "Standard"}
    ]
    with open("data/raw/campers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Name", "Age", "Medical", "Diet"])
        writer.writeheader()
        writer.writerows(campers)
        
    # 构建营地信息
    campsites = {
        "Whispering_Pines": {"zone": "A", "capacity": 4, "hazard_level": 2},
        "Bear_Claw_Ridge": {"zone": "B", "capacity": 4, "hazard_level": 5},
        "Eagle_Nest": {"zone": "C", "capacity": 3, "hazard_level": 1},
        "Hidden_Valley": {"zone": "C", "capacity": 5, "hazard_level": 4},
        "River_Bend": {"zone": "D", "capacity": 3, "hazard_level": 2}
    }
    with open("data/raw/campsites.json", "w") as f:
        json.dump(campsites, f, indent=4)
        
    # 构建库存信息
    inventory = {
        "Tents": 10,
        "Sleeping_Bags": 15,
        "First_Aid_Kits": 5,
        "Flashlights": 12
    }
    with open("data/raw/inventory.json", "w") as f:
        json.dump(inventory, f, indent=4)

def build_turn_2():
    os.makedirs("data/updates", exist_ok=True)
    
    # 构建天气警报：Zone C发生洪水。这会导致 Eagle_Nest 和 Hidden_Valley 不可用。
    # 之前在 Turn 1，由于 Eagle_Nest 是 hazard 1，很有可能把小孩安排在这里，现在必须把他们挤到 A 或 D 区。
    weather_alert = """<?xml version="1.0" encoding="UTF-8"?>
<alerts>
    <alert>
        <zone>C</zone>
        <type>Flash Flood Watch</type>
        <severity>Critical</severity>
        <instruction>Evacuate all campsites in this zone immediately.</instruction>
    </alert>
</alerts>
"""
    with open("data/updates/weather_alert.xml", "w") as f:
        f.write(weather_alert)
        
    # 构建物资未送达报告
    failed_delivery = {
        "Tents": 2,
        "Sleeping_Bags": 3,
        "Flashlights": 5
    }
    with open("data/updates/failed_delivery.json", "w") as f:
        json.dump(failed_delivery, f, indent=4)

def build_turn_3():
    os.makedirs("data/logs", exist_ok=True)
    
    # 构建事故日志，涉及特定的人员
    incidents = """[2024-07-15 14:30] Incident Report:
Camper Noah had a mild respiratory issue during the afternoon hike. Inhaler was used.
Camper Theodore tripped over a rock near the stream and sprained an ankle.
Camper Henry reported a tick bite, treated with basic first aid.
"""
    with open("data/logs/incident_reports.txt", "w") as f:
        f.write(incidents)

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
