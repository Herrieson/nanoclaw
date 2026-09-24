import os
import json
import csv

def build_env():
    os.makedirs("raw_data", exist_ok=True)

    certs_data = {
        "FiberOptic": ["John Doe", "Maria Garcia", "David Kim"],
        "Cat6": ["Maria Garcia", "Sarah Lee", "Tom Smith"],
        "Basic": ["Alex P", "John Doe", "Zack W"],
        "Safety": ["Linda B", "David Kim"]
    }

    with open("raw_data/certs.json", "w") as f:
        json.dump(certs_data, f, indent=4)

    signups_data = [
        ["Name", "Team", "Hours_Offered"],
        ["John Doe", "Network", "5"],
        ["Maria Garcia", "Network", "8"],
        ["Sarah Lee", "Cable", "-2"],   # Invalid negative hours
        ["Tom Smith", "Hardware", "4"],
        ["David Kim", "Network", "6"],
        ["Alex P", "Cleanup", "10"],    # Not certified for Fiber/Cat6
        ["Zack W", "Cable", "NaN"],     # Invalid string
        ["Linda B", "Support", "7"]     # Not certified for Fiber/Cat6
    ]

    with open("raw_data/signups.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(signups_data)

if __name__ == "__main__":
    build_env()
