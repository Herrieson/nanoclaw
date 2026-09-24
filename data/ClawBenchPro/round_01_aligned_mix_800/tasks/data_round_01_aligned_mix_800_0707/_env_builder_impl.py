import os
import json
import csv

def build_env():
    os.makedirs("tour_data", exist_ok=True)

    # 1. Manifest CSV
    manifest_data = [
        ["ticket_id", "passenger_name", "booking_date"],
        ["T-8801", "John Smith", "2023-10-01"],
        ["T-8802", "Alice Johnson", "2023-10-02"],
        ["T-8803", "Michael Brown", "2023-10-02"],
        ["T-8804", "Emily Davis", "2023-10-03"],
        ["T-8805", "David Wilson", "2023-10-04"],
        ["T-8806", "Sarah Miller", "2023-10-04"]
    ]
    with open("tour_data/manifest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(manifest_data)

    # 2. Waivers TXT (Missing T-8803 and T-8806)
    waivers_content = """Signed Waivers Log - DO NOT DELETE
T-8801
T-8804
Some garbled text here from the scanner
T-8805
T-8802
"""
    with open("tour_data/waivers.txt", "w") as f:
        f.write(waivers_content)

    # 3. Landmarks JSON (Lat and Lon swapped. Ohio is ~ Lat 39, Lon -82)
    landmarks_data = [
        {"id": 1, "name": "Pioneer Cabin", "lat": -82.104, "lon": 39.301},
        {"id": 2, "name": "Old Mill Ruins", "lat": -82.115, "lon": 39.312},
        {"id": 3, "name": "Native Earthworks", "lat": -82.130, "lon": 39.295},
        {"id": 4, "name": "Lookout Point", "lat": -82.142, "lon": 39.288}
    ]
    with open("tour_data/landmarks.json", "w") as f:
        json.dump(landmarks_data, f, indent=2)

if __name__ == "__main__":
    build_env()
