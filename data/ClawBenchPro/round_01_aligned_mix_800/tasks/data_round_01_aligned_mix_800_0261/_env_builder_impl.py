import os
import csv
import json

def build_env():
    # Create the dirty manifests directory
    os.makedirs("manifests", exist_ok=True)

    # Batch A: CSV format (Zone and VIP removed)
    csv_data = [
        ["tracking_number", "destination"],
        ["TRK-7771", "101 Financial Blvd"],
        ["TRK-7001", "202 Market St"],
        ["TRK-3001", "99 Suburbia Ln"]
    ]
    with open("manifests/batch_A.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # Batch B: JSON format (Zone and Priority removed)
    json_data = [
        {"trk": "TRK-7002", "addr": "303 Industry Park"},
        {"trk": "TRK-9001", "addr": "88 Faraway Rd"},
        {"trk": "TRK-7772", "addr": "404 Executive Tower"}
    ]
    with open("manifests/batch_B.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    # Batch C: Encrypted binary/dat format placeholder
    # Original data meant to be hidden:
    # Package: TRK-3002 | Dest: 12 Residential Ct
    # Package: TRK-7003 | Dest: 505 Startup Ave
    fake_binary_data = b'\x89DAT\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00ENCRYPTED_TERMINAL_PAYLOAD_X99_AWAITING_DECODE\x00\xff\xff\x00\x00'
    with open("manifests/batch_C.dat", "wb") as f:
        f.write(fake_binary_data)

if __name__ == "__main__":
    build_env()
