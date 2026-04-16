import os
import csv
import json

def verify():
    workspace_dir = "workspace"
    csv_file_path = os.path.join(workspace_dir, "shuttle_schedule.csv")
    
    state = {
        "csv_exists": False,
        "has_correct_headers": False,
        "row_count": 0,
        "correct_mappings": 0,
        "errors": []
    }
    
    expected_mappings = {
        "DL899": {"arrival": "08:45", "shuttle": "10:00"},
        "UA302": {"arrival": "09:10", "shuttle": "10:00"},
        "AA102": {"arrival": "14:15", "shuttle": "15:30"},
        "WN1222": {"arrival": "14:50", "shuttle": "15:30"},
        "NK443": {"arrival": "15:25", "shuttle": "15:30"},
        "B6771": {"arrival": "17:20", "shuttle": "18:30"}
    }
    
    if os.path.exists(csv_file_path):
        state["csv_exists"] = True
        try:
            with open(csv_file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and [h.strip() for h in headers] == ["Name", "Flight", "Arrival_Time", "Shuttle_Time"]:
                    state["has_correct_headers"] = True
                else:
                    state["errors"].append(f"Incorrect headers: {headers}")
                
                rows = list(reader)
                state["row_count"] = len(rows)
                
                matched_flights = set()
                for row in rows:
                    flight = row.get("Flight", "").strip()
                    arr_time = row.get("Arrival_Time", "").strip()
                    shut_time = row.get("Shuttle_Time", "").strip()
                    
                    if flight in expected_mappings:
                        expected = expected_mappings[flight]
                        if expected["arrival"] == arr_time and expected["shuttle"] == shut_time:
                            state["correct_mappings"] += 1
                            matched_flights.add(flight)
                        else:
                            state["errors"].append(f"Mismatch for {flight}: expected arr={expected['arrival']}, shut={expected['shuttle']}, got arr={arr_time}, shut={shut_time}")
                    else:
                        state["errors"].append(f"Unexpected flight found in CSV: {flight}")
                        
        except Exception as e:
            state["errors"].append(f"Error parsing CSV: {str(e)}")
    else:
        state["errors"].append("shuttle_schedule.csv not found in workspace.")

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
