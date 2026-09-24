import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("contracts", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 1. Contract Price List
    contract_prices = [
        ["item_id", "item_name", "contract_unit_price", "daily_usage_rate"],
        ["CHEM_001", "Industrial Bleach", 15.50, 0.5],
        ["WAX_002", "High-Gloss Floor Wax", 45.00, 0.2],
        ["MOP_003", "Microfiber Mop Head", 12.00, 0.1],
        ["BRUSH_004", "Scrub Brush", 8.25, 0.05],
        ["SOAP_005", "Antibacterial Hand Soap", 22.00, 1.2]
    ]
    with open("contracts/price_list.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(contract_prices)

    # 2. North Wing Inventory (Normal CSV)
    log_north = [
        ["date", "item_id", "supplier", "quantity", "unit_price_charged"],
        ["2023-10-01", "CHEM_001", "CleanCorp", 10, 15.50],
        ["2023-10-05", "WAX_002", "CleanCorp", 2, 50.00], # Overcharged by 5.00 each (Total 10.00)
        ["2023-10-10", "MOP_003", "Tools-R-Us", 5, 12.00],
    ]
    with open("inventory/north_wing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_north)

    # 3. South Wing - The "Obstacle" (Mocking a PDF file)
    # The actual data is hidden, Agent must use ocr_invoice_scanner_skill on this path.
    with open("inventory/south_wing_invoice.pdf", "w") as f:
        f.write("%PDF-1.4 [Binary Data - Use OCR Tool to Read]")

    # Hidden Data logic for the OCR Skill to return:
    # ["2023-10-02", "CHEM_001", "CleanCorp", 2, 16.00] -> Overcharge 1.00
    # ["2023-10-12", "SOAP_005", "CleanCorp", 1, 25.00] -> Overcharge 3.00
    # ["2023-10-15", "BRUSH_004", "CleanCorp", 3, 8.25] -> No overcharge
    
    # Final Overcharge: 10.0 (Wax) + 1.0 (Bleach) + 3.0 (Soap) = 14.00
    # Low stock (<5): WAX_002 (2), SOAP_005 (1), BRUSH_004 (3).

if __name__ == "__main__":
    build_env()
