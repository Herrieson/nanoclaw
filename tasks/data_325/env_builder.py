import os
import json
import zipfile
import csv

def build_env():
    base_dir = "assets/data_325"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "projects"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "records"), exist_ok=True)

    # 1. Create the zipped woodworking project
    plan_content = """Project: Cherry Wood Table
Difficulty: Intermediate
Notes: Make sure to sand with 220 grit before finishing.

Materials List:
- 4x Cherry Wood Planks (2x6)
- Wood Glue (Titebond III)
- 1.5 inch pocket hole screws
- Polyurethane finish
"""
    zip_path = os.path.join(base_dir, "projects", "backup_plans_v2.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("table_plan.txt", plan_content)
        zf.writestr("birdhouse.txt", "Materials: Pine, nails.")

    # 2. Create the messy hiking log
    hiking_log = """
[2023-05-12] Hiked the Kettle Moraine. Beautiful weather.
TRAIL: Kettle_Moraine_North | COORDS: 43.6822,-88.1345 | RATING: 4/5
[2023-06-01] Ope, got rained out.
[2023-06-15] Walked part of the Ice Age trail.
TRAIL: Ice_Age_Segment_B | COORDS: 44.1234,-89.5678 | RATING: 3/5
[2023-07-04] Finally did the big one.
TRAIL: Badger State Trail | COORDS: 42.6321,-89.6543 | RATING: 5/5
[2023-08-20] Mosquitoes were terrible today.
TRAIL: Devil's Lake Loop | COORDS: 43.4186,-89.7381 | RATING: 4/5
"""
    with open(os.path.join(base_dir, "logs", "hiking_logs.txt"), "w") as f:
        f.write(hiking_log)

    # 3. Create the CSV of invoices
    invoices = [
        {"InvoiceID": "INV-001", "Client": "Smith Builders", "Amount": "1500.00", "Status": "PAID"},
        {"InvoiceID": "INV-002", "Client": "Johnson LLC", "Amount": "3250.75", "Status": "UNPAID"},
        {"InvoiceID": "INV-003", "Client": "City of Milwaukee", "Amount": "500.00", "Status": "PAID"},
        {"InvoiceID": "INV-004", "Client": "Johnson LLC", "Amount": "1200.25", "Status": "UNPAID"},
        {"InvoiceID": "INV-005", "Client": "O'Connor Contracting", "Amount": "800.00", "Status": "UNPAID"},
    ]
    with open(os.path.join(base_dir, "records", "invoices.csv"), "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["InvoiceID", "Client", "Amount", "Status"])
        writer.writeheader()
        writer.writerows(invoices)

if __name__ == "__main__":
    build_env()
