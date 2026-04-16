import os
import csv
import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def verify():
    csv_path = "my_adventure_hikes.csv"
    state = {
        "csv_exists": False,
        "columns_correct": False,
        "row_count": 0,
        "data_accuracy": [],
        "overall_success": False
    }

    if not os.path.exists(csv_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f, indent=2)
        return

    state["csv_exists"] = True

    # Expected truth data
    home_lat = 34.7304
    home_lon = -86.5861
    
    # Book, lat, lon
    expected_data = {
        "Into the Wild": (63.8684, -149.0494),
        "Wild: From Lost to Found": (45.3694, -121.6944),
        "A Walk in the Woods": (35.5628, -83.4985),
        "Touching the Void": (-10.2750, -76.9000),
        "The Call of the Wild": (60.7331, -135.0506)
    }

    expected_distances = {}
    for book, coords in expected_data.items():
        expected_distances[book] = haversine(home_lat, home_lon, coords[0], coords[1])

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames == ["Book", "Latitude", "Longitude", "Distance_km"]:
            state["columns_correct"] = True
        
        correct_rows = 0
        for row in reader:
            state["row_count"] += 1
            book = row.get("Book", "").strip()
            # Match without asterisks if agent stripped them, or with if they kept them. 
            # We'll normalize by stripping asterisks.
            normalized_book = book.replace("*", "")
            
            if normalized_book in expected_data:
                try:
                    lat = float(row["Latitude"])
                    lon = float(row["Longitude"])
                    dist = float(row["Distance_km"])
                    
                    exp_lat, exp_lon = expected_data[normalized_book]
                    exp_dist = expected_distances[normalized_book]
                    
                    # Allow small floating point tolerances
                    lat_ok = abs(lat - exp_lat) < 0.001
                    lon_ok = abs(lon - exp_lon) < 0.001
                    dist_ok = abs(dist - exp_dist) < 5.0 # 5km tolerance due to earth radius variations in haversine implementations
                    
                    state["data_accuracy"].append({
                        "book": normalized_book,
                        "lat_ok": lat_ok,
                        "lon_ok": lon_ok,
                        "dist_ok": dist_ok
                    })
                    
                    if lat_ok and lon_ok and dist_ok:
                        correct_rows += 1
                except Exception:
                    pass

    if state["csv_exists"] and state["columns_correct"] and correct_rows == 5:
        state["overall_success"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
