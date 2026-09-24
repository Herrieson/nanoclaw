import os
import csv
import random

def build_env():
    os.makedirs("raw_data", exist_ok=True)
    
    dirty_data = [
        ["Trail_ID", "Marker_KM", "Issue_Type", "Severity_1_to_10", "Reporter_Notes"],
        ["T-01", "1.2", "Fallen Tree", "9", "Huge oak blocking the path entirely."],
        ["T-01", "2.5", "Clear", "1", "Looks good here."],
        ["T-02", "0.5", "Erosion", "8", "Trail washed out from the rain."],
        ["T-02", "invalid_km", "Fallen Tree", "10", "Wait where am I? My GPS broke."],
        ["T-03", "3.0", "Overgrowth", "4", "Needs some trimming."],
        ["T-03", "4.1", "Mudslide", "9", "Completely buried."],
        ["T-04", "1.1", "Fallen Tree", "8", "Branches everywhere."],
        ["T-05", "2.2", "Wasp Nest", "7", "Got stung twice."],
        ["T-06", "NaN", "Erosion", "9", "Forgot to log the KM"],
        ["T-07", "5.5", "Fallen Tree", "10", "Massive redwood down."]
    ]
    
    with open("raw_data/trail_logs_2023.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(dirty_data)

if __name__ == "__main__":
    build_env()
