import os
import csv

def build_env():
    base_dir = "assets/data_440"
    os.makedirs(base_dir, exist_ok=True)

    # Create the parts catalog
    catalog_path = os.path.join(base_dir, "parts_catalog.csv")
    with open(catalog_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Vehicle", "Part_Name", "Part_ID", "Bin_Location"])
        writer.writerow(["2015 Chevy Silverado", "Brake Pads", "BP-102", "A1"])
        writer.writerow(["2018 Ford F-150", "Transfer Case Motor", "TC-8892", "C4"])
        writer.writerow(["2020 Ram 1500", "Oil Filter", "OF-331", "B2"])
        writer.writerow(["2018 Ford F-150", "Alternator", "AL-901", "D1"])
        writer.writerow(["2018 Ford F-150", "Brake Rotors", "BR-404", "A3"])

    # Create the messy inventory logs
    log_content = """[2023-10-01] INVENTORY AUDIT COMPLETED. ALL COUNTS RESET TO 0.
[2023-10-02] RCV: 10 units of BP-102 from warehouse.
[2023-10-02] RCV: 4 units of TC-8892. Box was dented.
[2023-10-03] USE: 1 unit of TC-8892 on Work Order #441.
[2023-10-04] RCV: 5 units of OF-331.
[2023-10-04] SCRAP: 1 unit of BR-404. Rust damage.
[2023-10-05] USE: 2 units of BP-102.
[2023-10-06] USE: 1 unit of TC-8892. Mechanic: Dave. He complained about the fit.
[2023-10-07] SCRAP: 1 unit of TC-8892. Damaged in transit from the 10-02 delivery.
[2023-10-08] RCV: 2 units of AL-901.
[2023-10-08] ADJ: Found 1 extra unit of BP-102 under the shelf.
"""
    log_path = os.path.join(base_dir, "inventory_logs.txt")
    with open(log_path, "w") as f:
        f.write(log_content)

if __name__ == "__main__":
    build_env()
