import os
import json

def verify():
    base_dir = "."
    summary_path = os.path.join(base_dir, "summary.json")
    
    state = {
        "summary_file_exists": False,
        "is_valid_json": False,
        "total_distance_correct": False,
        "stops_correct": False,
        "distance_val": None,
        "stops_val": None
    }

    if os.path.exists(summary_path):
        state["summary_file_exists"] = True
        try:
            with open(summary_path, 'r') as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            dist = data.get("total_distance_km", 0)
            state["distance_val"] = dist
            
            # Expected distance: 
            # 43.00 to 43.01 (~1.1119 km)
            # 43.01 to 43.02 (~1.1119 km)
            # 43.02 to 43.03 (~1.1119 km)
            # 43.03 to 43.04 (~1.1119 km)
            # Total ~ 4.44 - 4.45 km
            if 4.40 <= dist <= 4.50:
                state["total_distance_correct"] = True
                
            stops = data.get("stops", [])
            state["stops_val"] = stops
            
            # Expected stops:
            # 1: lat 43.02, lon -87.00, duration 7 mins (08:03 to 08:10)
            # 2: lat 43.04, lon -87.00, duration 5 mins (08:15 to 08:20)
            if len(stops) == 2:
                s1, s2 = stops[0], stops[1]
                if (float(s1.get('lat', 0)) == 43.02 and s1.get('duration_minutes') == 7) and \
                   (float(s2.get('lat', 0)) == 43.04 and s2.get('duration_minutes') == 5):
                    state["stops_correct"] = True

        except Exception as e:
            pass

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
