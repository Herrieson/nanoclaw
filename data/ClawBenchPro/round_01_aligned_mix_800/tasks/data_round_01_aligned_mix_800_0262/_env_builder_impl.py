import os
import csv

def build_env():
    # Create necessary directories
    os.makedirs("dispatch", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. Create suspected plates list (only XYZ-9999 and ABC-1234 are actually stolen)
    with open("dispatch/suspect_plates.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Plate", "Reported_Date", "Owner", "Tip_Source"])
        writer.writerow(["XYZ-9999", "2023-10-01", "John Doe", "Anonymous"])
        writer.writerow(["LMN-4567", "2023-10-05", "Jane Smith", "Traffic Stop"])
        writer.writerow(["ABC-1234", "2023-10-08", "Carlos Ray", "Anonymous"])
        writer.writerow(["GHI-8888", "2023-10-10", "Sarah Connor", "Phone call"])

    # 2. Create messy speed logs
    # Expected Speeding Hotspot (Speed > 65): "Mile Marker 42" (3 speeders)
    # Expected Stolen Spotted: XYZ-9999, ABC-1234
    logs = [
        "08:00 AM | QWE-1111 | 55 | Main St Junction",
        "08:15 AM | XYZ-9999 | 60 | Elm Street Crossing", # Stolen, not speeding
        "08:22 AM | RTY-2222 | 70 | Mile Marker 42",      # Speeding
        "08:30 AM | UIO-3333 | 85 | Mile Marker 42",      # Speeding
        "08:45 AM | PAS-4444 | 68 | Downtown Avenue",     # Speeding
        "09:00 AM | ABC-1234 | 90 | Mile Marker 42",      # Stolen AND Speeding
        "09:15 AM | DFG-5555 | 75 | Elm Street Crossing", # Speeding
        "09:30 AM | HJK-6666 | 45 | Main St Junction",
        "09:45 AM | LZX-7777 | 66 | Downtown Avenue",     # Speeding
        "10:00 AM | LMN-4567 | 50 | Downtown Avenue",     # Suspect but NOT stolen (cleared)
    ]

    with open("dispatch/speed_logs.txt", "w") as f:
        f.write("--- DISPATCH AUTOMATED CAMERA LOGS ---\n")
        f.write("Time | License Plate | Recorded Speed | Location\n")
        for log in logs:
            f.write(log + "\n")

if __name__ == "__main__":
    build_env()
