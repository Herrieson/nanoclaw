import os
import json
import csv

def build_env():
    # Create directories
    os.makedirs("shifts", exist_ok=True)
    os.makedirs("sales", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # 1. Outdated Roster (Distractor)
    with open("roster.txt", "w") as f:
        f.write("Alice Henderson\nBob Jenkins\nOld Man Jenkins (Retired)")

    # 2. Shift Logs (CSV)
    # Approved: Alice Henderson, Bob Jenkins, Clara Smith, Diane O'Connor, Earl Thompson
    # Unauthorized: Frank Miller, Grace Kelly
    with open("shifts/day1_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Name", "Role"])
        writer.writerow(["08:00", "Alice Henderson", "Checkout"])
        writer.writerow(["10:00", "Frank Miller", "Floater"]) # Unauthorized
        writer.writerow(["12:00", "Bob Jenkins", "Greeter"])

    with open("shifts/day2_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Name", "Role"])
        writer.writerow(["09:00", "Clara Smith", "Checkout"])
        writer.writerow(["11:00", "Grace Kelly", "Floater"]) # Unauthorized
        writer.writerow(["14:00", "Diane O'Connor", "Greeter"])

    # 3. Sales Records (Mocking .scan files)
    # We create files that the OCR skill will "read"
    # Heritage: 15.25 (Pecan Pie) + 28.50 (Wooden Horse) = 43.75
    receipts = {
        "receipt_1001.scan": "CONTENT_RAW_8821: Item: Pioneer Pecan Pie | Cat: Heritage | Amt: 15.25",
        "receipt_1002.scan": "CONTENT_RAW_8822: Item: Diet Cola | Cat: General | Amt: 2.00",
        "receipt_1003.scan": "CONTENT_RAW_8823: Item: Hand-carved Wooden Horse | Cat: Heritage | Amt: 28.50",
        "receipt_1004.scan": "CONTENT_RAW_8824: Item: Bag of Chips | Cat: General | Amt: 5.50"
    }

    for filename, content in receipts.items():
        with open(os.path.join("sales", filename), "w") as f:
            f.write(content)

    # 4. Background noise
    with open("higgins_notes.txt", "w") as f:
        f.write("Note to self: Ensure all 'Heritage' items are taxed differently next year.")

if __name__ == "__main__":
    build_env()
