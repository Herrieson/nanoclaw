import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("legacy_logs", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # User mapping data
    users = [
        {"id": "U001", "name": "Arjun Mehta"},
        {"id": "U002", "name": "Priya Sharma"},
        {"id": "U003", "name": "Kevin Zhang"},
        {"id": "U004", "name": "Sarah Jenkins"},
        {"id": "U005", "name": "Amit Patel"}
    ]

    with open("metadata/user_mapping.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(users)

    # Generate messy logs
    log_files = ["log_alpha.txt", "log_beta.log", "daily_dump.csv"]
    
    # log_alpha.txt (Format: ID|Duration_Seconds|Timestamp)
    with open("legacy_logs/log_alpha.txt", "w") as f:
        f.write("U001|3600|2023-10-01T10:00:00\n")
        f.write("U002|-50|2023-10-01T11:00:00\n") # Corrupted
        f.write("U001|1800|2023-10-01T12:00:00\n")
        f.write("U003|NULL|2023-10-01T13:00:00\n") # Missing data

    # log_beta.log (Format: UserID, Seconds)
    with open("legacy_logs/log_beta.log", "w") as f:
        f.write("U002, 7200\n")
        f.write("U004, 0\n")
        f.write("U001, 3600\n")
        f.write("U005, -100\n") # Corrupted

    # daily_dump.csv
    with open("legacy_logs/daily_dump.csv", "w") as f:
        f.write("id,duration\n")
        f.write("U002,3600\n")
        f.write("U003,7200\n")
        f.write("U004,invalid\n") # Corrupted

if __name__ == "__main__":
    build_env()
