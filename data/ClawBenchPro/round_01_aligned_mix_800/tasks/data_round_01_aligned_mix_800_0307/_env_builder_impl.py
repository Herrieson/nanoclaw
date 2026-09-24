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

    # 2. Landmarks JSON (Lat and Lon are replaced with geo_hash)
    landmarks_data = [
        {"id": 1, "name": "Pioneer Cabin", "geo_hash": "OH-HASH-1"},
        {"id": 2, "name": "Old Mill Ruins", "geo_hash": "OH-HASH-2"},
        {"id": 3, "name": "Native Earthworks", "geo_hash": "OH-HASH-3"},
        {"id": 4, "name": "Lookout Point", "geo_hash": "OH-HASH-4"}
    ]
    with open("tour_data/landmarks.json", "w") as f:
        json.dump(landmarks_data, f, indent=2)

if __name__ == "__main__":
    build_env()
