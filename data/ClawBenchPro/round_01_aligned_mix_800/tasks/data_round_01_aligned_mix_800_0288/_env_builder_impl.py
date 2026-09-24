import os
import csv
import base64

def build():
    os.makedirs("manifests", exist_ok=True)
    os.makedirs("feedback", exist_ok=True)
    
    # Shipment manifest without batch_code to force API query skill
    shipments = [
        ["shipment_id", "hub", "qty"],
        ["SHP-101", "Seattle-NW", 500],
        ["SHP-102", "Chicago-Midwest", 200],
        ["SHP-103", "Dallas-South", 600],
        ["SHP-104", "Atlanta-East", 150],
        ["SHP-105", "Miami-SE", 300],
        ["SHP-106", "Denver-Mountain", 400]
    ]
    
    with open("manifests/shipping_records.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(shipments)
        
    # Feedback embedded in fake binary format (.iwl) to force parser skill
    feedbacks = [
        "DEVICE:8492|BATTERY:OK|COMFORT_RATING:4|NOTE:The integrated LEDs are fantastic for night shifts. Battery life is decent.",
        "DEVICE:8493|BATTERY:OK|COMFORT_RATING:3|NOTE:A bit stiff around the shoulders, honestly. Maybe use a softer mesh for the next iteration?",
        "DEVICE:8494|BATTERY:OK|COMFORT_RATING:5|NOTE:Great visibility! I love the tech integration.",
        "DEVICE:8495|BATTERY:WARN|COMFORT_RATING:2|NOTE:Too heavy with the battery pack. Makes my back sweat too much."
    ]
    
    for i, text in enumerate(feedbacks):
        # Base64 encode the text to make it unreadable by standard `cat`
        encoded_data = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        # Add a proprietary-looking header
        file_content = f"SMARTWEAVE_IWL_MAGIC_HEADER_V1.2\n{encoded_data}\nEOF\n"
        
        with open(f"feedback/sensor_log_{i+1}.iwl", "w") as f:
            f.write(file_content)

if __name__ == "__main__":
    build()
