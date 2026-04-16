import os
import csv
import json

def build_env():
    base_dir = "assets/data_264"
    data_dir = os.path.join(base_dir, "client_data")
    os.makedirs(data_dir, exist_ok=True)

    # Press A Data (CSV)
    # E-001: 3 events (60 mins)
    # E-002: 2 events (30 mins)
    # E-005: 1 event (30 mins)
    # Total A = 120 mins
    csv_file = os.path.join(data_dir, "press_A_telemetry.csv")
    csv_data = [
        {"timestamp": "2023-10-01T08:15:00", "fault_code": "E-001", "downtime_minutes": 20},
        {"timestamp": "2023-10-02T09:10:00", "fault_code": "E-005", "downtime_minutes": 30},
        {"timestamp": "2023-10-02T14:05:00", "fault_code": "E-001", "downtime_minutes": 15},
        {"timestamp": "2023-10-03T11:20:00", "fault_code": "E-002", "downtime_minutes": 10},
        {"timestamp": "2023-10-05T16:45:00", "fault_code": "E-002", "downtime_minutes": 20},
        {"timestamp": "2023-10-06T07:30:00", "fault_code": "E-001", "downtime_minutes": 25},
    ]
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "fault_code", "downtime_minutes"])
        writer.writeheader()
        writer.writerows(csv_data)

    # Press B Data (JSON)
    # E-003: 5 events (60 mins)
    # E-001: 4 events (60 mins)
    # E-002: 4 events (60 mins)
    # Total B = 180 mins
    json_file = os.path.join(data_dir, "press_B_telemetry.json")
    json_data = [
        {"event_time": "2023-10-01", "error": "E-003", "duration_min": 10},
        {"event_time": "2023-10-01", "error": "E-003", "duration_min": 10},
        {"event_time": "2023-10-02", "error": "E-001", "duration_min": 5},
        {"event_time": "2023-10-02", "error": "E-002", "duration_min": 15},
        {"event_time": "2023-10-03", "error": "E-001", "duration_min": 15},
        {"event_time": "2023-10-04", "error": "E-002", "duration_min": 15},
        {"event_time": "2023-10-04", "error": "E-003", "duration_min": 15},
        {"event_time": "2023-10-05", "error": "E-002", "duration_min": 15},
        {"event_time": "2023-10-06", "error": "E-003", "duration_min": 20},
        {"event_time": "2023-10-06", "error": "E-001", "duration_min": 10},
        {"event_time": "2023-10-07", "error": "E-002", "duration_min": 15},
        {"event_time": "2023-10-07", "error": "E-003", "duration_min": 5},
        {"event_time": "2023-10-08", "error": "E-001", "duration_min": 30},
    ]
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    build_env()
