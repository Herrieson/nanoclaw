import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("shifts", exist_ok=True)
    os.makedirs("sales", exist_ok=True)
    
    # Distractor file
    with open("oklahoma_dustbowl_notes.txt", "w") as f:
        f.write("Just some personal reading notes on the 1930s Dust Bowl. Fascinating history.\nNeeds more research on local agricultural impact.")

    # Create the roster (whitelist)
    roster = ["Alice Henderson", "Bob Jenkins", "Clara Smith", "Diane O'Connor", "Earl Thompson"]
    with open("roster.txt", "w") as f:
        for name in roster:
            f.write(name + "\n")

    # Create shift logs (CSV)
    # Day 1 includes an unapproved person: "Frank Miller"
    with open("shifts/day1_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Name", "Role"])
        writer.writerow(["08:00", "Alice Henderson", "Checkout"])
        writer.writerow(["10:00", "Frank Miller", "Floater"])
        writer.writerow(["12:00", "Bob Jenkins", "Greeter"])

    # Day 2 includes an unapproved person: "Grace Kelly"
    with open("shifts/day2_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Name", "Role"])
        writer.writerow(["09:00", "Clara Smith", "Checkout"])
        writer.writerow(["11:00", "Grace Kelly", "Floater"])
        writer.writerow(["14:00", "Diane O'Connor", "Greeter"])
        writer.writerow(["16:00", "Alice Henderson", "Cleanup"])

    # Create sales records (JSON)
    # Heritage items total: 15.25 + 28.50 = 43.75
    # General items total: 2.00 + 5.50 = 7.50
    sales_data = [
        {"receipt_id": "1001", "item_name": "Pioneer Pecan Pie", "category": "Heritage", "amount": 15.25},
        {"receipt_id": "1002", "item_name": "Diet Cola", "category": "General", "amount": 2.00},
        {"receipt_id": "1003", "item_name": "Hand-carved Wooden Horse", "category": "Heritage", "amount": 28.50},
        {"receipt_id": "1004", "item_name": "Bag of Chips", "category": "General", "amount": 5.50}
    ]

    for data in sales_data:
        file_path = os.path.join("sales", f"receipt_{data['receipt_id']}.json")
        with open(file_path, "w") as f:
            json.dump(data, f)

if __name__ == "__main__":
    build_env()
