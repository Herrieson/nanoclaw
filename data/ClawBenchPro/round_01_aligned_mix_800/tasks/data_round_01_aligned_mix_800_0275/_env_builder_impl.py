import os
import json
import csv

def build_env():
    # Create directory structure
    os.makedirs("mezclas/spectra", exist_ok=True)
    os.makedirs("resultados", exist_ok=True)

    # File 1: JSON format (Normal)
    # Good: B101 (14%), Bad: B103 (18%)
    with open("mezclas/log_A.json", "w", encoding="utf-8") as f:
        json.dump([
            {"batch_id": "B101", "wood": "Cherry", "volume_l": 50, "red_pigment_pct": 14},
            {"batch_id": "B102", "wood": "Oak", "volume_l": 100, "red_pigment_pct": 25},
            {"batch_id": "B103", "wood": "Cherry", "volume_l": 150, "red_pigment_pct": 18}
        ], f, indent=2)

    # File 2: CSV format (Missing pigment, requires Spectro Skill)
    # Bad: B105 (Needs analysis -> 16%), Good: B106 (Needs analysis -> 12%)
    with open("mezclas/log_B.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "wood_type", "vol_l", "spectrum_file"])
        writer.writerow(["B104", "Walnut", 80, "sensor_b104.dat"])
        writer.writerow(["B105", "Cherry", 20, "sensor_b105.dat"])
        writer.writerow(["B106", "Cherry", 200, "sensor_b106.dat"])

    # Create dummy binary spectra files
    for bid in ["b104", "b105", "b106"]:
        with open(f"mezclas/spectra/sensor_{bid}.dat", "wb") as f:
            f.write(os.urandom(1024)) # Dummy binary data

    # File 3: Pipe-separated TXT format (Missing volume, requires Inventory Skill)
    # Good: B107 (14%), Bad: B108 (20%)
    with open("mezclas/log_C.txt", "w", encoding="utf-8") as f:
        f.write("Batch|Type|RedPct\n")
        f.write("B107|Cherry|14\n")
        f.write("B108|Cherry|20\n")
        f.write("B109|Pine|18\n")

if __name__ == "__main__":
    build_env()
