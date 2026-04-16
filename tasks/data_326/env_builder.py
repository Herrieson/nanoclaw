import os
import csv
import random

def build_env():
    base_dir = "assets/data_326/raw_data"
    os.makedirs(base_dir, exist_ok=True)
    
    # File 1: Standard format, with header
    with open(os.path.join(base_dir, "batch_01.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Ticker", "Side", "Qty", "Price"])
        writer.writerow(["2023-10-01", "AAPL", "BUY", "100", "150.50"])
        writer.writerow(["2023-10-01", "BRK.A", "BUY", "2", "520000.00"])
        writer.writerow(["2023-10-02", "MSFT", "SELL", "50", "330.00"])

    # File 2: MM/DD/YYYY format, no header
    with open(os.path.join(base_dir, "batch_02.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["10/03/2023", "TSLA", "BUY", "200", "250.00"])
        writer.writerow(["10/04/2023", "BRK.A", "SELL", "1", "525000.00"])
        writer.writerow(["10/05/2023", "GOOG", "BUY", "300", "135.20"])

    # File 3: YYYY/MM/DD format, with header, weird spacing
    with open(os.path.join(base_dir, "batch_03.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([" trade_date ", " sym ", " direction ", " amount ", " execution_price "])
        writer.writerow([" 2023/10/06 ", " NVDA ", " BUY ", " 150 ", " 450.00 "])
        writer.writerow([" 2023/10/07 ", " BRK.A ", " BUY ", " 3 ", " 518000.00 "])
        writer.writerow([" 2023/10/08 ", " AAPL ", " SELL ", " 100 ", " 152.00 "])

if __name__ == "__main__":
    build_env()
