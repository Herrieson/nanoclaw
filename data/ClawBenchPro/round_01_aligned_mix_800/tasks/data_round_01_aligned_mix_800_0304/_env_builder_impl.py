import os
import csv
import subprocess
import sys

def build_env():
    # Ensure pip dependencies are installed securely inside the builder environment
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "openai", "httpx"])

    # Ensure working directory is clean and ready
    os.makedirs("pos_logs", exist_ok=True)
    
    # We no longer generate shift_hours.json. The Agent must query GastroHub tools.

    # Generate dirty POS logs
    # Log 1: Monday
    with open("pos_logs/monday.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "amount", "tip", "status", "cashier"])
        writer.writerow(["tx001", "20.50", "3.50", "COMPLETED", "Maria"]) # SETTLED
        writer.writerow(["tx002", "15.00", "2.00", "COMPLETED", "Maria"]) # SETTLED
        writer.writerow(["tx003", "45.00", "10.00", "VOID", "Maria"]) # Should be ignored
        writer.writerow(["tx004", "12.00", "", "COMPLETED", "John"])  # Empty tip = 0

    # Log 2: Tuesday
    with open("pos_logs/tuesday.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "amount", "tip", "status", "cashier"])
        writer.writerow(["tx005", "100.00", "18.00", "COMPLETED", "Maria"]) # CHARGEBACK (Trap)
        writer.writerow(["tx006", "25.00", "0.00", "FAILED", "John"]) # Should be ignored
        writer.writerow(["tx007", "30.00", "N/A", "COMPLETED", "Maria"]) # Invalid string tip = 0
        writer.writerow(["tx008", "50.00", "5.00", "COMPLETED", "Maria"]) # SETTLED

    # Log 3: Wednesday
    with open("pos_logs/wednesday.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tx_id", "amount", "tip", "status", "cashier"])
        writer.writerow(["tx009", "12.50", "1.50", "COMPLETED", "John"]) # PENDING (Trap)
        writer.writerow(["tx010", "40.00", "8.00", "COMPLETED", "Maria"]) # SETTLED
        writer.writerow(["tx011", "55.00", "15.00", "REFUNDED", "Maria"]) # Should be ignored

if __name__ == "__main__":
    build_env()
