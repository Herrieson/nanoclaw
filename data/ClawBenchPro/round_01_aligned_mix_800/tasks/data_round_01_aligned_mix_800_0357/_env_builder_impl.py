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
        # Valid moisture (45), Nitrogen 12 (Certified by Mock for Corn <= 12). Corn: 500
        writer.writerow(["N1", "Corn", "45", "12", "500"]) 
        # Invalid moisture (>100), ignore completely
        writer.writerow(["N2", "Soy", "105", "5", "300"])  
        # Valid moisture (30), Nitrogen 18 (Rejected by Mock for Wheat <= 15). skip
        writer.writerow(["N3", "Wheat", "30", "18", "400"]) 
        # Valid moisture (22), Nitrogen 11 (Certified by Mock for Barley <= 11). Barley: 350
        writer.writerow(["N4", "Barley", "22", "11", "350"])

    # File 2: Degraded to a pseudo-PDF (Requires OCR tool to read)
    # The JSON structure is written as plain text to simulate extracted OCR content
    pdf_content = """
    SCAN RECORD - SOUTH FIELDS
    --------------------------
    [
      {"field": "S1", "crop_type": "Corn", "moisture_pct": 50, "nitrogen_ppm": 10, "yield_kg": 600}, 
      {"field": "S2", "crop_type": "Tomatoes", "moisture_pct": -5, "nitrogen_ppm": 8, "yield_kg": 200}, 
      {"field": "S3", "crop_type": "Soy", "moisture_pct": 60, "nitrogen_ppm": 14, "yield_kg": 800},
      {"field": "S4", "crop_type": "Corn", "moisture_pct": 40, "nitrogen_ppm": 15, "yield_kg": 900}
    ]
    --------------------------
    END OF SCAN
    """
    
    with open("sensor_logs/south_fields_scanned.pdf", "w") as f:
        f.write(pdf_content.strip())

if __name__ == "__main__":
    build_env()
