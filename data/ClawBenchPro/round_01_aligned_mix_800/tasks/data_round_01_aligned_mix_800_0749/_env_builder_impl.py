import os
import csv

def build_env():
    os.makedirs("requests", exist_ok=True)
    os.makedirs("warehouse_logs", exist_ok=True)

    # Generate initial requests data
    requests_data = {
        "Oakridge Elementary": {"No. 2 Pencils (Box)": 50, "Blank Canvas": 10, "Notebooks": 30},
        "Pine View Middle": {"Binders": 20, "Calculators": 15},
        "Cedar High": {"Acrylic Paint": 5, "Sketchbooks": 25, "Backpacks": 10},
        "Maple Academy": {"Erasers": 100, "Rulers": 40}
    }

    for school, items in requests_data.items():
        filename = f"requests/{school.lower().replace(' ', '_')}.txt"
        with open(filename, "w") as f:
            f.write(f"Donation Request for {school}\n")
            f.write("-----------------------------\n")
            for item, qty in items.items():
                f.write(f"{item}: {qty}\n")

    # Generate warehouse pull logs with intentional discrepancies
    # Oakridge: missing 10 pencils, missing 2 blank canvas
    # Pine View: 0 missing
    # Cedar High: missing 5 backpacks
    # Maple Academy: missing 10 erasers, missing 5 rulers
    csv_data = [
        ["Date", "School", "Item", "Qty_Pulled"],
        ["2023-10-01", "Oakridge Elementary", "No. 2 Pencils (Box)", 40],
        ["2023-10-01", "Oakridge Elementary", "Blank Canvas", 8],
        ["2023-10-01", "Oakridge Elementary", "Notebooks", 30],
        ["2023-10-02", "Pine View Middle", "Binders", 20],
        ["2023-10-02", "Pine View Middle", "Calculators", 15],
        ["2023-10-03", "Cedar High", "Acrylic Paint", 5],
        ["2023-10-03", "Cedar High", "Sketchbooks", 25],
        ["2023-10-03", "Cedar High", "Backpacks", 5],
        ["2023-10-04", "Maple Academy", "Erasers", 90],
        ["2023-10-04", "Maple Academy", "Rulers", 35]
    ]

    with open("warehouse_logs/pull_records.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
