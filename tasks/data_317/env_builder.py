import os
import csv
import json

def build_env():
    base_dir = "assets/data_317"
    dumps_dir = os.path.join(base_dir, "gadget_dumps")
    os.makedirs(dumps_dir, exist_ok=True)

    # Sleep data (CSV format) - Date format YYYY-MM-DD
    # We want matches where Sleep < 70 AND Posture > 15
    # Matches: 2023-10-01 (HR 75), 2023-10-04 (HR 85), 2023-10-05 (HR 80)
    # Expected Avg HR = (75 + 85 + 80) / 3 = 80
    sleep_data = [
        {"Date": "2023-10-01", "Sleep_Score": "65", "Avg_HR": "75"}, # Match
        {"Date": "2023-10-02", "Sleep_Score": "80", "Avg_HR": "70"}, # No match (Sleep high)
        {"Date": "2023-10-03", "Sleep_Score": "60", "Avg_HR": "80"}, # No match (Posture low)
        {"Date": "2023-10-04", "Sleep_Score": "50", "Avg_HR": "85"}, # Match
        {"Date": "2023-10-05", "Sleep_Score": "68", "Avg_HR": "80"}, # Match
        {"Date": "2023-10-06", "Sleep_Score": "90", "Avg_HR": "65"}, # No match
    ]

    with open(os.path.join(dumps_dir, "garmin_sleep_export.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Sleep_Score", "Avg_HR"])
        writer.writeheader()
        writer.writerows(sleep_data)

    # Posture data (JSON format) - Date format MM/DD/YYYY (different to trap simple joins)
    posture_data = [
        {"date": "10/01/2023", "posture_deviation_pct": 18},
        {"date": "10/02/2023", "posture_deviation_pct": 20},
        {"date": "10/03/2023", "posture_deviation_pct": 10},
        {"date": "10/04/2023", "posture_deviation_pct": 22},
        {"date": "10/05/2023", "posture_deviation_pct": 16},
        {"date": "10/06/2023", "posture_deviation_pct": 12},
    ]

    with open(os.path.join(dumps_dir, "smart_shirt_log.json"), "w") as f:
        json.dump(posture_data, f, indent=4)
        
    # Noise file
    with open(os.path.join(dumps_dir, "oura_raw.txt"), "w") as f:
        f.write("2023-10-01: readiness 80\n2023-10-02: readiness 85\n")

if __name__ == "__main__":
    build_env()
