import os
import csv
import struct

def build_env():
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Create safety_protocols.pdf (Mocked as a text file for simplicity in builder, but name implies PDF complexity)
    # In a real scenario, we'd use a PDF lib, but here we provide a text-readable "PDF" content
    # that an Agent would typically use a PDF tool to read.
    with open("safety_protocols.pdf", "w") as f:
        f.write("%PDF-1.4\n")
        f.write("ACTIVE MONITORING LIST:\n")
        for r in ["R-101", "R-102", "R-105", "R-202"]:
            f.write(f"REACTOR_ID: {r}\n")
        f.write("%%EOF")
    
    # 2. Good CSV data (Standard)
    with open("logs/batch_alpha.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "reactor_id", "temp_c", "total_weight_kg", "recycled_content_kg", "output_product_kg"])
        writer.writerow(["B001", "R-101", 195.5, 1000, 200, 950]) # Pass
        writer.writerow(["B002", "R-101", 225.0, 1000, 180, 940]) # Fail: Temp
        writer.writerow(["B003", "R-999", 180.0, 500, 100, 480])  # Ignore: Inactive Reactor

    # 3. Proprietary Binary Data (.dat)
    # Format: 4s (BatchID), 8s (Reactor), f (Temp), f (Weight), f (Recycled), f (Output)
    def write_dat(filename, records):
        with open(filename, "wb") as f:
            for r in records:
                # Padding strings to fixed length
                bid = r[0].ljust(4).encode('ascii')
                rid = r[1].ljust(8).encode('ascii')
                f.write(struct.pack("4s8sffff", bid, rid, r[2], r[3], r[4], r[5]))

    # B004: Fail Green (100/2000=5%), B005: Pass
    write_dat("logs/batch_beta.dat", [
        ("B004", "R-102", 205.0, 2000.0, 100.0, 1900.0),
        ("B005", "R-105", 218.0, 1500.0, 300.0, 1450.0)
    ])

    # 4. Another CSV with edge cases
    with open("logs/batch_gamma.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "reactor_id", "temp_c", "total_weight_kg", "recycled_content_kg", "output_product_kg"])
        writer.writerow(["B006", "R-202", 230.1, 800, 50, 750])   # Fail: Temp & Green
        writer.writerow(["B007", "R-102", 190.0, 1000, 150, 990]) # Pass (Exactly 15%)
        writer.writerow(["B008", "R-105", 210.0, 1200, 100, 1100]) # Fail: Green

if __name__ == "__main__":
    build_env()
