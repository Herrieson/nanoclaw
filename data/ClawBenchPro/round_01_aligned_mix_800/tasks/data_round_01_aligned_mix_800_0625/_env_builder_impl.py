import os
import csv

def build_env():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Vetted volunteers whitelist
    whitelist = [
        "Alice Smith",
        "Bob Johnson",
        "Charlie Davis",
        "Diana Prince",
        "Eve Adams"
    ]
    with open("data/whitelist.txt", "w", encoding="utf-8") as f:
        for name in whitelist:
            f.write(f"{name}\n")

    # Dirty logs data
    logs_data = [
        ["Name", "Family_Type", "Hours"],
        ["Alice Smith", "Under 5", "4.5"],       # Valid: 4.5
        ["Bob Johnson", "Elderly", "3.0"],       # Ignore: Not Under 5
        ["Charlie Davis", "Under 5", "2.5"],     # Valid: 2.5
        ["Diana Prince", "Under 5", "-1.0"],     # Ignore: Negative hours
        ["Eve Adams", "Under 5", "3.0"],         # Valid: 3.0
        ["Frank Castle", "Under 5", "5.0"],      # Ignore: Not in whitelist. Flag as unauthorized.
        ["Grace Lee", "Adults", "2.0"],          # Ignore: Not in whitelist. Flag as unauthorized.
        ["Alice Smith", "Under 5", "2.0"],       # Valid: 2.0
        ["Eve Adams", "Under 5", "invalid"],     # Ignore: String instead of number
        ["Henry Todd", "Under 5", "1.5"]         # Ignore: Not in whitelist. Flag as unauthorized.
    ]
    
    with open("data/logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(logs_data)

if __name__ == "__main__":
    build_env()
