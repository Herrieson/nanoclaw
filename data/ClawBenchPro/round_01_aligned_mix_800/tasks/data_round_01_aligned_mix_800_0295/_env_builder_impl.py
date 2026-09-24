import os
import json
import csv
import base64

def build_env():
    # Create directories
    os.makedirs("schedules", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0295", exist_ok=True)

    # 1. Official Schedules (CSV) - Names removed for privacy obstacle
    schedule_data = [
        ["employee_id", "scheduled_hours"],
        ["E001", "40"],
        ["E002", "20"],
        ["E003", "30"]
    ]
    with open("schedules/weekly_plan.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(schedule_data)

    # 2. Weekend fragment
    with open("schedules/weekend_shift.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows([["employee_id", "scheduled_hours"], ["E005", "8"]])

    # 3. Raw Logs (JSON-lines style but messy, then encoded)
    # Alice (E001): 42 hours (within 10% limit)
    # Bob (E002): 25 hours (Exceeds 20 hours + 10% = 22 hours) -> Flag
    # Dave (E004): 5 hours (Not in schedule) -> Ghost
    logs = [
        {"id": "E001", "hours": 20},
        {"id": "E001", "hours": 22},
        {"id": "E002", "hours": 15},
        {"id": "E002", "hours": 10}, 
        {"id": "E004", "hours": 5},
        "CORRUPT_DATA_ROW_###_999", # Dirty data to test robustness
        {"id": "E003", "hours": 30}
    ]
    
    # Construct raw log string
    log_str = ""
    for entry in logs:
        if isinstance(entry, dict):
            log_str += json.dumps(entry) + "\n"
        else:
            log_str += entry + "\n"
            
    # Obfuscate to binary (Base64) to force skill usage
    encoded_logs = base64.b64encode(log_str.encode('utf-8'))
    with open("raw_logs/punch_clock.bin", "wb") as f:
        f.write(encoded_logs)

if __name__ == "__main__":
    build_env()
