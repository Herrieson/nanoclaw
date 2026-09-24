import os
import json
import csv

def build_env():
    # Create directories
    os.makedirs("schedules", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Official Schedules (CSV)
    # Alice: 40 hours, Bob: 20 hours, Charlie: 30 hours
    schedule_data = [
        ["employee_id", "name", "scheduled_hours"],
        ["E001", "Alice", "40"],
        ["E002", "Bob", "20"],
        ["E003", "Charlie", "30"]
    ]
    with open("schedules/weekly_plan.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(schedule_data)

    # 2. Raw Logs (JSON-lines style but messy)
    # Alice: 42 hours (within 10% limit)
    # Bob: 25 hours (Exceeds 20 hours + 10% = 22 hours) -> Flag
    # Dave: 5 hours (Not in schedule) -> Ghost
    # Some dirty data included
    logs = [
        {"id": "E001", "name": "Alice", "hours": 20},
        {"id": "E001", "name": "Alice", "hours": 22},
        {"id": "E002", "name": "Bob", "hours": 15},
        {"id": "E002", "name": "Bob", "hours": 10}, # Total 25
        {"id": "E004", "name": "Dave", "hours": 5},  # Ghost
        "CORRUPT_DATA_ROW_###_999", # Dirty data
        {"id": "E003", "name": "Charlie", "hours": 30}
    ]
    
    with open("raw_logs/punch_clock_raw.log", "w") as f:
        for entry in logs:
            if isinstance(entry, dict):
                f.write(json.dumps(entry) + "\n")
            else:
                f.write(entry + "\n")

    # 3. Another schedule fragment to test multi-file handling
    with open("schedules/weekend_shift.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows([["employee_id", "name", "scheduled_hours"], ["E005", "Eve", "8"]])

if __name__ == "__main__":
    build_env()
