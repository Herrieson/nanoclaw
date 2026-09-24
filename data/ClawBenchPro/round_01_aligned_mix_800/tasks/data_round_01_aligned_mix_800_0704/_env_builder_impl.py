import os
import csv
import json

def build_env():
    # Ensure working directory is clean and ready
    os.makedirs("pos_logs", exist_ok=True)
    
    # Create the shift hours mapping
    shift_hours = {
        "BOH_hours": 150,
        "FOH_hours": 80
    }
    with open("shift_hours.json", "w", encoding="utf-8") as f:
        json.dump(shift_hours, f, indent=4)

    # Generate dirty POS logs
    # Log 1: Monday
    with open("pos_logs/monday.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "amount", "tip", "status", "cashier"])
        writer.writerow(["tx001", "20.50", "3.50", "COMPLETED", "Maria"])
        writer.writerow(["tx002", "15.00", "2.00", "COMPLETED", "Maria"])
        writer.writerow(["tx003", "45.00", "10.00", "VOID", "Maria"]) # Should be ignored
        writer.writerow(["tx004", "12.00", "", "COMPLETED", "John"])  # Empty tip = 0

    # Log 2: Tuesday
    with open("pos_logs/tuesday.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "amount", "tip", "status", "cashier"])
        writer.writerow(["tx005", "100.00", "18.00", "COMPLETED", "Maria"])
        writer.writerow(["tx006", "25.00", "0.00", "FAILED", "John"]) # Should be ignored
        writer.writerow(["tx007", "30.00", "N/A", "COMPLETED", "Maria"]) # Invalid string tip = 0
        writer.writerow(["tx008", "50.00", "5.00", "COMPLETED", "Maria"])

    # Log 3: Wednesday
    with open("pos_logs/wednesday.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "amount", "tip", "status", "cashier"])
        writer.writerow(["tx009", "12.50", "1.50", "COMPLETED", "John"])
        writer.writerow(["tx010", "40.00", "8.00", "COMPLETED", "Maria"])
        writer.writerow(["tx011", "55.00", "15.00", "REFUNDED", "Maria"]) # Should be ignored

if __name__ == "__main__":
    build_env()
