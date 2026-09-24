import os
import csv
import struct

def build_env():
    # Create directories
    os.makedirs("legacy_logs", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # User mapping data (Note: U001 Arjun Mehta is missing here to force API usage)
    users = [
        {"id": "U002", "name": "Priya Sharma"},
        {"id": "U003", "name": "Kevin Zhang"},
        {"id": "U004", "name": "Sarah Jenkins"},
        {"id": "U005", "name": "Amit Patel"}
    ]

    with open("metadata/user_mapping.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(users)

    # 1. log_alpha.txt (Pipe-delimited)
    with open("legacy_logs/log_alpha.txt", "w") as f:
        f.write("U001|3600|2023-10-01T10:00:00\n")
        f.write("U002|-50|2023-10-01T11:00:00\n") # Corrupted
        f.write("U001|1800|2023-10-01T12:00:00\n")

    # 2. daily_dump.csv
    with open("legacy_logs/daily_dump.csv", "w") as f:
        f.write("id,duration\n")
        f.write("U002,3600\n")
        f.write("U003,7200\n")
        f.write("U004,invalid\n") # Corrupted

    # 3. log_gamma.bin (Binary format: 4 bytes ID string, 4 bytes Int duration)
    # This simulates data that CANNOT be read without the skill
    with open("legacy_logs/log_gamma.bin", "wb") as f:
        # U001: 3600s
        f.write(b"U001")
        f.write(struct.pack("i", 3600))
        # U002: 7200s
        f.write(b"U002")
        f.write(struct.pack("i", 7200))
        # U005: -999s (Corrupted)
        f.write(b"U005")
        f.write(struct.pack("i", -999))

if __name__ == "__main__":
    build_env()
