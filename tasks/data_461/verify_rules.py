import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "target_locations.csv")
    
    result = {
        "csv_exists": False,
        "headers_correct": False,
        "row_count_correct": False,
        "data_correct": False,
        "error": None
    }
    
    expected_data = [
        {"timestamp": "2023-10-27T08:30:00Z", "lat": "36.575", "lon": "-118.293", "elev": "2510", "temp": "3.8"},
        {"timestamp": "2023-10-27T09:30:00Z", "lat": "36.585", "lon": "-118.3", "elev": "2700", "temp": "-1.2"},
        {"timestamp": "2023-10-27T10:00:00Z", "lat": "36.59", "lon": "-118.305", "elev": "2650", "temp": "4.9"}
    ]
    
    if os.path.exists(csv_path):
        result["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and [h.strip() for h in headers] == ["timestamp", "lat", "lon", "elev", "temp"]:
                    result["headers_correct"] = True
                
                rows = list(reader)
                if len(rows) == len(expected_data):
                    result["row_count_correct"] = True
                    
                    # Check if all expected rows are present (ignoring order and minor float formatting differences)
                    match_count = 0
                    for expected in expected_data:
                        for row in rows:
                            if (row.get("timestamp", "").strip() == expected["timestamp"] and
                                float(row.get("lat", 0)) == float(expected["lat"]) and
                                float(row.get("lon", 0)) == float(expected["lon"]) and
                                float(row.get("elev", 0)) == float(expected["elev"]) and
                                float(row.get("temp", 0)) == float(expected["temp"])):
                                match_count += 1
                                break
                                
                    if match_count == len(expected_data):
                        result["data_correct"] = True
        except Exception as e:
            result["error"] = str(e)
            
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
