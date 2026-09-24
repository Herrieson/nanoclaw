import os
import csv

def build_env():
    # Create necessary directories
    os.makedirs("daily_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Create daily log files with some target data and noise
    logs = {
        "log_monday.txt": "Morning check. Weather is crisp.\nSheep-092 seems fine and is eating well.\nCow-104: fever, isolated in pen 3.\nNeed to fix the fence near the creek.",
        "log_tuesday.txt": "Pig-33 is growing fast.\nChecked the north pasture, grass is getting low.\nHorse-07 limping after the morning trail ride, calling the vet.",
        "log_wednesday.txt": "Normal day. Cow-105 healthy.\nFound a stray dog near the barn, scared the chickens.\nGoat-12 is stubborn as usual.",
        "log_thursday.txt": "Heavy rain today. Barn roof is leaking slightly.\nSheep-099 looking a bit tired but no fever.\nAll animals accounted for.",
    }

    for filename, content in logs.items():
        with open(os.path.join("daily_logs", filename), "w") as f:
            f.write(content)

    # Create feed invoices CSV
    invoices = [
        ["Date", "Item", "Weight_lbs", "Cost"],
        ["2023-10-01", "Alfalfa", "1500", "300"],
        ["2023-10-05", "Corn", "800", "120"],
        ["2023-10-12", "Alfalfa", "2200", "440"],
        ["2023-10-15", "Oats", "500", "100"],
        ["2023-10-20", "Alfalfa", "1000", "200"],
    ]

    with open("feed_invoices.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(invoices)

if __name__ == "__main__":
    build_env()
