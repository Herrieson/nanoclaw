import os
import json
import binascii
import random
import string

def build_env():
    base_dir = "assets/data_417"
    os.makedirs(base_dir, exist_ok=True)

    # Generate the JSON file for sneaker releases
    releases = [
        {"sku": "SKU-1001", "name": "Retro High OG", "hype_score": 85},
        {"sku": "SKU-1002", "name": "Everyday Kicks", "hype_score": 45},
        {"sku": "SKU-1003", "name": "Boost 350 V3", "hype_score": 92},
        {"sku": "SKU-1004", "name": "Skate Slip-On", "hype_score": 60},
        {"sku": "SKU-1005", "name": "Dunk Low Panda", "hype_score": 88},
        {"sku": "SKU-1006", "name": "Running Trainer X", "hype_score": 30}
    ]

    with open(os.path.join(base_dir, "releases.json"), "w") as f:
        json.dump(releases, f, indent=2)

    # The actual scanned inventory contains a mix of hyped and non-hyped shoes, 
    # but notably missing SKU-1003 (so they shouldn't just grab all hyped shoes from the JSON).
    scanned_skus = ["SKU-1001", "SKU-1002", "SKU-1005", "SKU-1006"]
    dump_lines = []

    # Format of the dump: SCAN_RECORD|[random_8_chars]|[hex_encoded_sku]|[random_4_chars]
    for sku in scanned_skus:
        hex_sku = binascii.hexlify(sku.encode('utf-8')).decode('utf-8')
        pad1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        pad2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        dump_lines.append(f"SCAN_RECORD|{pad1}|{hex_sku}|{pad2}")

    # Add some noise records (invalid SKUs to test decoding logic)
    for _ in range(4):
        noise = ''.join(random.choices(string.ascii_letters, k=8))
        hex_noise = binascii.hexlify(noise.encode('utf-8')).decode('utf-8')
        pad1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        pad2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        dump_lines.append(f"SCAN_RECORD|{pad1}|{hex_noise}|{pad2}")

    # Shuffle the dump lines so they are unordered
    random.shuffle(dump_lines)

    # Write the hex dump file
    with open(os.path.join(base_dir, "rfid_dump.txt"), "w") as f:
        f.write("\n".join(dump_lines))

if __name__ == "__main__":
    build_env()
