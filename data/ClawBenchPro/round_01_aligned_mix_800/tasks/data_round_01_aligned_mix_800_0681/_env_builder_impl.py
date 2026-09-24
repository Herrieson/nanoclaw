import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("contracts", exist_ok=True)
    
    # Create the contract price list
    contract_prices = [
        ["item_id", "item_name", "contract_unit_price"],
        ["CHEM_001", "Industrial Bleach", 15.50],
        ["WAX_002", "High-Gloss Floor Wax", 45.00],
        ["MOP_003", "Microfiber Mop Head", 12.00],
        ["BRUSH_004", "Scrub Brush", 8.25],
        ["SOAP_005", "Antibacterial Hand Soap", 22.00]
    ]
    with open("contracts/price_list.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(contract_prices)

    # Create messy inventory logs
    # Log 1: North Wing Storage
    log_north = [
        ["date", "item_id", "supplier", "quantity", "unit_price_charged"],
        ["2023-10-01", "CHEM_001", "CleanCorp", 10, 15.50],
        ["2023-10-05", "WAX_002", "CleanCorp", 2, 50.00], # Overcharged by 5.00 each (Total 10.00)
        ["2023-10-10", "MOP_003", "Tools-R-Us", 5, 12.00],
        ["2023-10-12", "SOAP_005", "CleanCorp", 1, 25.00], # Overcharged by 3.00 each (Total 3.00)
    ]
    
    # Log 2: South Wing Storage (Low stock check)
    log_south = [
        ["date", "item_id", "supplier", "quantity", "unit_price_charged"],
        ["2023-10-02", "CHEM_001", "CleanCorp", 2, 16.00], # Overcharged by 0.50 each (Total 1.00)
        ["2023-10-08", "BRUSH_004", "CleanCorp", 3, 8.25],
        ["2023-10-15", "WAX_002", "CleanCorp", 1, 45.00],
    ]

    with open("inventory/north_wing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_north)
        
    with open("inventory/south_wing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_south)

    # Total overcharge calculation:
    # WAX_002: (50-45)*2 = 10.00
    # SOAP_005: (25-22)*1 = 3.00
    # CHEM_001: (16-15.5)*2 = 1.00
    # Total = 14.00

    # Stock levels:
    # CHEM_001: 10 + 2 = 12
    # WAX_002: 2 + 1 = 3 (LOW)
    # MOP_003: 5
    # SOAP_005: 1 (LOW)
    # BRUSH_004: 3 (LOW)

if __name__ == "__main__":
    build_env()
