import os
import csv
import random

def build_env():
    base_dir = "assets/data_53"
    os.makedirs(base_dir, exist_ok=True)
    
    timesheets_dir = os.path.join(base_dir, "timesheets")
    os.makedirs(timesheets_dir, exist_ok=True)
    
    # Roster
    roster = [
        {"id": "E01", "name": "Alice Johnson"},
        {"id": "E02", "name": "Bob Smith"},
        {"id": "E03", "name": "Charlie Davis"},
        {"id": "E04", "name": "Diana Ross"},
        {"id": "E05", "name": "Evan Wright"}
    ]
    
    with open(os.path.join(base_dir, "roster.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(roster)
        
    # Generate timesheets
    # E01: Perfect punches, > 40 hours
    # E02: Perfect punches, < 40 hours
    # E03: Missing an OUT punch one day
    # E04: Missing an OUT punch, > 40 hours without it? No, keep it simple
    # E05: Perfect
    
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    
    punches = {
        "monday": [
            ("E01", "IN", "08:00"), ("E01", "OUT", "17:00"), # 9
            ("E02", "IN", "09:00"), ("E02", "OUT", "14:00"), # 5
            ("E03", "IN", "10:00"), ("E03", "OUT", "18:00"), # 8
            ("E04", "IN", "07:30"), ("E04", "OUT", "15:30"), # 8
            ("E05", "IN", "11:00"), ("E05", "OUT", "16:00")  # 5
        ],
        "tuesday": [
            ("E01", "IN", "08:00"), ("E01", "OUT", "17:00"), # 9
            ("E02", "IN", "09:00"), ("E02", "OUT", "14:00"), # 5
            ("E03", "IN", "10:00"), # Missing OUT! (0 hours for today)
            ("E04", "IN", "07:30"), ("E04", "OUT", "15:30"), # 8
            ("E05", "IN", "11:00"), ("E05", "OUT", "16:00")  # 5
        ],
        "wednesday": [
            ("E01", "IN", "08:00"), ("E01", "OUT", "17:00"), # 9
            ("E02", "IN", "09:00"), ("E02", "OUT", "14:00"), # 5
            ("E03", "IN", "10:00"), ("E03", "OUT", "18:00"), # 8
            ("E04", "IN", "07:30"), ("E04", "OUT", "15:30"), # 8
            ("E05", "IN", "11:00"), ("E05", "OUT", "16:00")  # 5
        ],
        "thursday": [
            ("E01", "IN", "08:00"), ("E01", "OUT", "17:00"), # 9
            ("E02", "IN", "09:00"), ("E02", "OUT", "14:00"), # 5
            ("E03", "IN", "10:00"), ("E03", "OUT", "18:00"), # 8
            ("E04", "IN", "07:30"), ("E04", "OUT", "15:30"), # 8
            ("E05", "IN", "11:00"), ("E05", "OUT", "16:00")  # 5
        ],
        "friday": [
            ("E01", "IN", "08:00"), ("E01", "OUT", "17:00"), # 9  (Total: 45) -> Overtime
            ("E02", "IN", "09:00"), ("E02", "OUT", "14:00"), # 5  (Total: 25)
            ("E03", "IN", "10:00"), ("E03", "OUT", "18:00"), # 8  (Total: 32)
            ("E04", "IN", "07:30"), ("E04", "OUT", "15:30"), # 8  (Total: 40)
            ("E05", "IN", "11:00"), ("E05", "OUT", "16:00")  # 5  (Total: 25)
        ]
    }
    
    for day, punch_list in punches.items():
        # Shuffle to ensure the agent has to group/sort them
        random.shuffle(punch_list)
        with open(os.path.join(timesheets_dir, f"{day}.log"), "w") as f:
            for p in punch_list:
                f.write(f"{p[0]}|{p[1]}|{p[2]}\n")

if __name__ == "__main__":
    build_env()
