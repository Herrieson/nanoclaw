import os
import csv
import json

def build_env():
    # Create the directory for raw sensor logs
    os.makedirs("sensor_logs", exist_ok=True)

    # File 1: CSV format from the North Fields
    with open("sensor_logs/north_fields.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["field_id", "crop_type", "moisture_pct", "nitrogen_ppm", "yield_kg"])
        # Valid, included. Corn: 500
        writer.writerow(["N1", "Corn", "45", "12", "500"]) 
        # Invalid moisture (>100), ignore completely
        writer.writerow(["N2", "Soy", "105", "5", "300"])  
        # Valid data, but high nitrogen (>= 15), skip for organic yield
        writer.writerow(["N3", "Wheat", "30", "18", "400"]) 
        # Valid, included. Barley: 350
        writer.writerow(["N4", "Barley", "22", "11", "350"])

    # File 2: JSON format from the South Fields
    with open("sensor_logs/south_fields.json", "w") as f:
        json.dump([
            # Valid. Corn: 600
            {"field": "S1", "crop_type": "Corn", "moisture_pct": 50, "nitrogen_ppm": 10, "yield_kg": 600}, 
            # Invalid moisture (<0)
            {"field": "S2", "crop_type": "Tomatoes", "moisture_pct": -5, "nitrogen_ppm": 8, "yield_kg": 200}, 
            # Valid. Soy: 800
            {"field": "S3", "crop_type": "Soy", "moisture_pct": 60, "nitrogen_ppm": 14, "yield_kg": 800},
            # Valid data, but nitrogen exactly 15 (must be strictly under 15), skip
            {"field": "S4", "crop_type": "Corn", "moisture_pct": 40, "nitrogen_ppm": 15, "yield_kg": 900}
        ], f, indent=2)

if __name__ == "__main__":
    build_env()
