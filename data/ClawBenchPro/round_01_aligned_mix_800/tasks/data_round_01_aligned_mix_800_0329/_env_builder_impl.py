import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("contractor_logs", exist_ok=True)
    os.makedirs("accounting", exist_ok=True)

    # File 1: CSV format (Standard)
    csv_data = [
        ["Name", "LaborCost", "MaterialCost"],
        ["Apex Framing", "2500.0", "4000.0"],
        ["Rogue Welding", "1200.0", "800.0"],
        ["Desert Fox Concrete", "3100.5", "6200.0"]
    ]
    with open("contractor_logs/site_a_invoices.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # File 2: PDF placeholder (Simulated need for PDF Tool)
    # Content: Baja Dirt Works, Labor: 3000.0, Materials: 1500.0
    with open("contractor_logs/site_c_invoice.pdf", "w") as f:
        f.write("%PDF-1.4 [SIMULATED PDF CONTENT]\nContractor: Baja Dirt Works\nLabor Cost: 3000.0\nMaterial Cost: 1500.0")

    # File 3: OCR Placeholder (Simulated scanned image)
    # Content: Maverick Excavation, Labor: 4000.0, Materials: 1000.0
    with open("contractor_logs/site_b_contract_scan.ocr", "w") as f:
        f.write("--- SCAN_START ---\nVENDOR: Maverick Excavation\nLABOR_AMT: 4000.0\nMAT_AMT: 1000.0\n--- SCAN_END ---")

    # File 4: Distractor
    with open("contractor_logs/notes.txt", "w") as f:
        f.write("Check the ramps for splinters. Also, buy more Monster Energy.")

if __name__ == "__main__":
    build_env()
