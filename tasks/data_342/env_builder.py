import os
import json
import csv

def build_env():
    base_dir = "assets/data_342"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "energy_logs"), exist_ok=True)

    # 1. Properties
    properties = [
        {"id": "B100", "address": "123 Maple St", "sq_ft": 10000},
        {"id": "B200", "address": "456 Oak Ave", "sq_ft": 5000},
        {"id": "B300", "address": "789 Pine Blvd", "sq_ft": 20000}
    ]
    with open(os.path.join(base_dir, "properties.json"), "w") as f:
        json.dump(properties, f, indent=2)

    # 2. Energy Logs (Monthly kWh)
    # B100: avg ~ 12000 -> 1.2 per sq_ft
    b100_data = [11800, 12100, 11900, 12050, 12200, 11950]
    # B200: avg ~ 11000 -> 2.2 per sq_ft (WORST OFFENDER)
    b200_data = [10800, 11200, 10900, 11100, 11050, 10950]
    # B300: avg ~ 18000 -> 0.9 per sq_ft
    b300_data = [17800, 18200, 18000, 17900, 18100, 18000]

    for b_id, data in [("B100", b100_data), ("B200", b200_data), ("B300", b300_data)]:
        with open(os.path.join(base_dir, f"energy_logs/{b_id}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["month", "kwh"])
            for i, val in enumerate(data, 1):
                writer.writerow([f"2023-0{i}", val])

    # 3. Tenants
    tenants = [
        {"building_id": "B100", "unit": "1A", "first_name": "John", "last_name": "Doe"},
        {"building_id": "B100", "unit": "1B", "first_name": "Jane", "last_name": "Smith"},
        {"building_id": "B200", "unit": "101", "first_name": "Alice", "last_name": "Johnson"},
        {"building_id": "B200", "unit": "102", "first_name": "Bob", "last_name": "Williams"},
        {"building_id": "B200", "unit": "201", "first_name": "Charlie", "last_name": "Brown"},
        {"building_id": "B300", "unit": "PH1", "first_name": "Diana", "last_name": "Prince"},
    ]
    with open(os.path.join(base_dir, "tenants.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["building_id", "unit", "first_name", "last_name"])
        writer.writeheader()
        writer.writerows(tenants)

if __name__ == "__main__":
    build_env()
