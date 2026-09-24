import os
import json
import csv

def build_env():
    # The cwd is already set to the task's root, so we use pure relative paths.
    os.makedirs("mezclas", exist_ok=True)

    # File 1: JSON format
    with open("mezclas/log_A.json", "w", encoding="utf-8") as f:
        json.dump([
            {"batch_id": "B101", "wood": "Cherry", "volume_l": 50, "red_pigment_pct": 14},
            {"batch_id": "B102", "wood": "Oak", "volume_l": 100, "red_pigment_pct": 25},
            {"batch_id": "B103", "wood": "Cherry", "volume_l": 150, "red_pigment_pct": 18}
        ], f, indent=2)

    # File 2: CSV format
    with open("mezclas/log_B.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "wood_type", "vol_l", "red_pct"])
        writer.writerow(["B104", "Walnut", 80, 2])
        writer.writerow(["B105", "Cherry", 20, 16])
        writer.writerow(["B106", "Cherry", 200, 12])

    # File 3: Pipe-separated TXT format
    with open("mezclas/log_C.txt", "w", encoding="utf-8") as f:
        f.write("Batch|Type|Liters|RedPct\n")
        f.write("B107|Cherry|10|14\n")
        f.write("B108|Cherry|100|20\n")
        f.write("B109|Pine|500|18\n")

if __name__ == "__main__":
    build_env()
