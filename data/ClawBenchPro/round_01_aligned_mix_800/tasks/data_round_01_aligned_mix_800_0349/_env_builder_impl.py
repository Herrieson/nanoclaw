import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("requests", exist_ok=True)
    os.makedirs("warehouse_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)

    # 1. School Requests - Represented as PDF files (Placeholders)
    # Metadata for the Mock OCR Skill to read
    requests_content = {
        "Oakridge Elementary": {"No. 2 Pencils (Box)": 50, "Blank Canvas": 10, "Notebooks": 30},
        "Pine View Middle": {"Binders": 20, "Calculators": 15},
        "Cedar High": {"Acrylic Paint": 5, "Sketchbooks": 25, "Backpacks": 10},
        "Maple Academy": {"Erasers": 100, "Rulers": 40}
    }
    
    for school in requests_content.keys():
        filename = f"requests/{school.lower().replace(' ', '_')}.pdf"
        with open(filename, "w") as f:
            f.write(f"%PDF-1.4 (Mock scan of handwritten request for {school})")
            
    # Save the 'ground truth' for the OCR skill to use internally
    with open("metadata/ocr_ground_truth.json", "w") as f:
        json.dump(requests_content, f)

    # 2. SKU Mapping for the Warehouse Skill
    sku_mapping = {
        "SKU-7701-A": "No. 2 Pencils (Box)",
        "SKU-7702-B": "Blank Canvas",
        "SKU-7703-C": "Notebooks",
        "SKU-8801-X": "Binders",
        "SKU-8802-Y": "Calculators",
        "SKU-9901-Z": "Acrylic Paint",
        "SKU-9902-W": "Sketchbooks",
        "SKU-9903-Q": "Backpacks",
        "SKU-1101-M": "Erasers",
        "SKU-1102-N": "Rulers"
    }
    with open("metadata/sku_master_list.json", "w") as f:
        json.dump(sku_mapping, f)

    # 3. Warehouse Pull Logs (using SKUs)
    # Oakridge: pulled 40 pencils (short 10), 8 canvas (short 2), 30 notebooks (ok)
    # Pine View: pulled 20 binders (ok), 15 calculators (ok)
    # Cedar: pulled 5 paint (ok), 25 sketchbooks (ok), 5 backpacks (short 5)
    # Maple: pulled 90 erasers (short 10), 35 rulers (short 5)
    csv_data = [
        ["Date", "School", "SKU_ID", "Qty_Pulled"],
        ["2023-10-01", "Oakridge Elementary", "SKU-7701-A", 40],
        ["2023-10-01", "Oakridge Elementary", "SKU-7702-B", 8],
        ["2023-10-01", "Oakridge Elementary", "SKU-7703-C", 30],
        ["2023-10-02", "Pine View Middle", "SKU-8801-X", 20],
        ["2023-10-02", "Pine View Middle", "SKU-8802-Y", 15],
        ["2023-10-03", "Cedar High", "SKU-9901-Z", 5],
        ["2023-10-03", "Cedar High", "SKU-9902-W", 25],
        ["2023-10-03", "Cedar High", "SKU-9903-Q", 5],
        ["2023-10-04", "Maple Academy", "SKU-1101-M", 90],
        ["2023-10-04", "Maple Academy", "SKU-1102-N", 35]
    ]

    with open("warehouse_logs/pull_records.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
