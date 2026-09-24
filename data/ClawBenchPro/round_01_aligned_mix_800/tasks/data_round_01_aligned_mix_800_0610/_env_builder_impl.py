import os
import json
import csv

def build_env():
    # Create the messy dump directory
    os.makedirs("gadget_dumps", exist_ok=True)

    # Generate Solar Panel Logs (CSV)
    # Total kwh for january: 12 + 15 + 18 = 45
    with open("gadget_dumps/solar_january.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["day", "kwh_generated"])
        writer.writerow(["1", "12"])
        writer.writerow(["2", "15"])
        writer.writerow(["3", "18"])
        
    # Total kwh for february: 20 + 22 + 13 = 55
    # Grand total solar: 100
    with open("gadget_dumps/solar_february.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["day", "kwh_generated"])
        writer.writerow(["1", "20"])
        writer.writerow(["2", "22"])
        writer.writerow(["3", "13"])

    # Generate Water Monitor Logs (JSON)
    # Total gallons for front: 40 + 60 = 100
    with open("gadget_dumps/water_sensor_front.json", "w") as f:
        json.dump({
            "sensor": "front", 
            "readings": [{"gallons_saved": 40}, {"gallons_saved": 60}]
        }, f)

    # Total gallons for back: 75 + 25 = 100
    # Grand total water: 200
    with open("gadget_dumps/water_sensor_back.json", "w") as f:
        json.dump({
            "sensor": "back", 
            "readings": [{"gallons_saved": 75}, {"gallons_saved": 25}]
        }, f)

    # Generate noise/interference files to test the Agent's filtering
    with open("gadget_dumps/grocery_receipt.txt", "w") as f:
        f.write("Milk: $3.99\nEggs: $2.50\nOrganic Bread: $5.00\nTotal: $11.49")

    with open("gadget_dumps/tech_news_article.txt", "w") as f:
        f.write("The latest smart home gadgets of 2023 are focusing heavily on eco-friendly integrations. Consumers are excited...")

if __name__ == "__main__":
    build_env()
