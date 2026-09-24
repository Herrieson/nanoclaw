import os

def build_env():
    # Create required directories
    os.makedirs("inventory_logs", exist_ok=True)
    os.makedirs("project_planning", exist_ok=True)

    # Generate messy CSV log
    csv_content = """Species, Thickness(in), Width(in), Length(in), Condition
White Oak, 2, 6, 48, Usable
Red Oak, 1, 8, 72, Usable
White Oak, 1, 10, 60, Warped
White Oak, 2, 4, 36, Usable
Pine, 2, 4, 96, Usable
"""
    with open("inventory_logs/week1_shipment.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    # Generate weird shorthand text log
    txt_content = """[LOG ENTRY: 10/24] Item: White Oak | Dims: 1.5x8x96 | Status: Usable
[LOG ENTRY: 10/24] Item: Maple | Dims: 2x4x48 | Status: Usable
[LOG ENTRY: 10/25] Item: White Oak | Dims: 2x12x72 | Status: Split
[LOG ENTRY: 10/26] Item: Walnut | Dims: 1x8x36 | Status: Usable
[LOG ENTRY: 10/26] Item: White Oak | Dims: 1x6x24 | Status: Usable
"""
    with open("inventory_logs/week2_shipment.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

if __name__ == "__main__":
    build_env()
