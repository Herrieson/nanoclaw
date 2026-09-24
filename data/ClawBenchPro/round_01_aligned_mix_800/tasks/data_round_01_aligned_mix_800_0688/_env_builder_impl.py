import os
import csv

def build():
    os.makedirs("manifests", exist_ok=True)
    os.makedirs("feedback", exist_ok=True)
    
    shipments = [
        ["shipment_id", "hub", "batch_code", "qty"],
        ["SHP-101", "Seattle-NW", "V1-Standard", 500],
        ["SHP-102", "Chicago-Midwest", "V2-Neon", 200],
        ["SHP-103", "Dallas-South", "V1-Standard", 600],
        ["SHP-104", "Atlanta-East", "V2-Neon", 150],
        ["SHP-105", "Miami-SE", "V3-Pro", 300],
        ["SHP-106", "Denver-Mountain", "V1-Standard", 400]
    ]
    
    with open("manifests/shipments.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(shipments)
        
    feedbacks = [
        "The integrated LEDs are fantastic for night shifts. Comfort rating: 4. Battery life is decent.",
        "A bit stiff around the shoulders, honestly. Comfort rating: 3. Maybe use a softer mesh for the next iteration?",
        "Great visibility! Comfort rating: 5. I love the tech integration.",
        "Too heavy with the battery pack. Comfort rating: 2. Makes my back sweat too much."
    ]
    
    for i, text in enumerate(feedbacks):
        with open(f"feedback/tester_log_{i+1}.txt", "w") as f:
            f.write(text)

if __name__ == "__main__":
    build()
