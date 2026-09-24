import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # Safety protocols - list of active reactors
    active_reactors = ["R-101", "R-102", "R-105", "R-202"]
    with open("safety_protocols.txt", "w") as f:
        f.write("ACTIVE MONITORING LIST:\n")
        for r in active_reactors:
            f.write(f"{r}\n")
    
    # Generate noisy data
    # 1. Good CSV data
    with open("logs/batch_alpha.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "reactor_id", "temp_c", "total_weight_kg", "recycled_content_kg", "output_product_kg"])
        writer.writerow(["B001", "R-101", 195.5, 1000, 200, 950]) # Pass
        writer.writerow(["B002", "R-101", 225.0, 1000, 180, 940]) # Fail: Temp
        writer.writerow(["B003", "R-999", 180.0, 500, 100, 480])  # Ignore: Inactive Reactor

    # 2. Messy text data
    with open("logs/batch_beta.txt", "w") as f:
        f.write("BatchID: B004 | Reactor: R-102 | Temp: 205 | Weight: 2000 | Recycled: 100 | Output: 1900\n") # Fail: Green (100/2000 = 5%)
        f.write("BatchID: B005 | Reactor: R-105 | Temp: 218 | Weight: 1500 | Recycled: 300 | Output: 1450\n") # Pass
    
    # 3. Another CSV with edge cases
    with open("logs/batch_gamma.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "reactor_id", "temp_c", "total_weight_kg", "recycled_content_kg", "output_product_kg"])
        writer.writerow(["B006", "R-202", 230.1, 800, 50, 750])   # Fail: Temp & Green
        writer.writerow(["B007", "R-102", 190.0, 1000, 150, 990]) # Pass (Exactly 15%)
        writer.writerow(["B008", "R-105", 210.0, 1200, 100, 1100]) # Fail: Green

if __name__ == "__main__":
    build_env()
