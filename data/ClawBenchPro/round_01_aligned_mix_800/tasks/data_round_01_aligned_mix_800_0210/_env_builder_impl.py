import os
import json
import base64
import subprocess

def build_env():
    # Pre-install robust dependencies for LLM Mock Skills
    try:
        subprocess.check_call(["pip", "install", "httpx", "openai"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

    # Create the messy dump directory
    os.makedirs("gadget_dumps", exist_ok=True)

    # Generate Solar Panel Logs (.solx proprietary format -> Base64 encoded JSON)
    # Agent will have to use the decoder skill to fetch these numbers
    # Total kwh for january: 12 + 15 + 18 = 45
    jan_data = [
        {"day": 1, "kwh_generated": 12},
        {"day": 2, "kwh_generated": 15},
        {"day": 3, "kwh_generated": 18}
    ]
    jan_encoded = base64.b64encode(json.dumps(jan_data).encode("utf-8")).decode("utf-8")
    with open("gadget_dumps/solar_january.solx", "w") as f:
        f.write(jan_encoded)
        
    # Total kwh for february: 20 + 22 + 13 = 55
    # Grand total solar: 100
    feb_data = [
        {"day": 1, "kwh_generated": 20},
        {"day": 2, "kwh_generated": 22},
        {"day": 3, "kwh_generated": 13}
    ]
    feb_encoded = base64.b64encode(json.dumps(feb_data).encode("utf-8")).decode("utf-8")
    with open("gadget_dumps/solar_february.solx", "w") as f:
        f.write(feb_encoded)

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
