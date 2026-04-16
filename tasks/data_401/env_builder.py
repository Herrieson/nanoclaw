import os
import csv

def build_env():
    base_dir = "assets/data_401"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create project dimensions file
    dimensions_content = """
Project: Casa Verde
Sketched: Last Night

Room Measurements:
Kitchen: 12ft x 15ft
Living Room: 20ft x 25ft
Master Bedroom: 16ft x 18ft
Guest Bedroom: 10ft x 12ft
Bathrooms (Total): 8ft x 10ft
"""
    with open(os.path.join(base_dir, "project_dimensions.txt"), "w", encoding="utf-8") as f:
        f.write(dimensions_content)
        
    # Expected area:
    # Kitchen: 180
    # Living Room: 500
    # Master Bed: 288
    # Guest Bed: 120
    # Bathrooms: 80
    # Total = 1168 sq ft

    # 2. Create raw suppliers CSV
    csv_data = [
        ["SupplierName", "Material", "PricePerSqFt", "Currency", "InStock"],
        ["BuildIt Right", "Concrete", "4.50", "USD", "Yes"],
        ["Cemex Mex", "Concrete", "80.00", "MXN", "Yes"],       # 80/20 = 4.00 (Cheapest Concrete)
        ["Solid Foundations", "Concrete", "3.90", "USD", "No"],   # Out of stock
        ["LumberJacks", "Lumber", "3.20", "USD", "No"],         # Out of stock
        ["WoodWorks", "Lumber", "3.50", "USD", "Yes"],          # Cheapest in-stock Lumber
        ["Madera Fina", "Lumber", "75.00", "MXN", "Yes"],       # 75/20 = 3.75
        ["Acero Mex", "Steel", "120.00", "MXN", "Yes"],         # 120/20 = 6.00
        ["US Steel Co", "Steel", "5.80", "USD", "Yes"],         # Cheapest in-stock Steel
        ["Iron Giants", "Steel", "5.50", "USD", "No"],          # Out of stock
        ["GlassMasters", "Glass", "12.00", "USD", "Yes"]        # Irrelevant material
    ]

    with open(os.path.join(base_dir, "suppliers_raw.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
