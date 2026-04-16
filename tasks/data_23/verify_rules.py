import os
import json

def verify():
    target_file = "airport_runs_summary.json"
    state = {
        "file_exists": False,
        "valid_json": False,
        "total_miles_correct": False,
        "total_fare_correct": False,
        "trips_count_correct": False,
        "extracted_miles": None,
        "extracted_fare": None,
        "extracted_trips_count": None
    }
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Expected values based on env_builder.py
            # Trips from 10-11 to 10-13 containing "airport", "airprt", "air-port"
            # 1. [2023-10-11 09:15] Trip: Hotel California to LAX Airport. Miles: 18.5. Fare: $45.00. Tip: $5.00.
            # 2. [2023-10-12 14:20] Trip: Staples Center to Burbank airprt. Miles: 15.0. Fare: $38.00. Tip: $6.00.
            # 3. [2023-10-13 18:45] Trip: Anaheim to John Wayne Air-port. Miles: 40.2. Fare: $85.00. Tip: $15.00. Cash tip, nice!
            # Total Miles = 18.5 + 15.0 + 40.2 = 73.7
            # Total Fare = 45.00 + 38.00 + 85.00 = 168.0
            
            expected_miles = 73.7
            expected_fare = 168.0
            expected_count = 3
            
            state["extracted_miles"] = data.get("total_miles")
            state["extracted_fare"] = data.get("total_fare")
            state["extracted_trips_count"] = len(data.get("trips", []))
            
            if state["extracted_miles"] == expected_miles:
                state["total_miles_correct"] = True
            if state["extracted_fare"] == expected_fare:
                state["total_fare_correct"] = True
            if state["extracted_trips_count"] == expected_count:
                state["trips_count_correct"] = True
                
        except Exception as e:
            pass

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == "__main__":
    verify()
