import sys
import json
import os

def run(complex_name):
    os.makedirs("logs", exist_ok=True)
    with open("logs/modern_tracker_usage.log", "a") as f:
        f.write(f"Called for: {complex_name}\n")

    if "Oakwood" in complex_name:
        return json.dumps({"empty_stations": 7, "status": "synchronized"})
    return json.dumps({"error": "Complex not found"})

if __name__ == "__main__":
    print(run(sys.argv[1] if len(sys.argv) > 1 else ""))
