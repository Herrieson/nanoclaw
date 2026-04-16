import os
import csv

def build_env():
    base_dir = "assets/data_409"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Pricing Notes (Unstructured text)
    pricing_content = """
    Prices for this season:
    Standard lawn mowing - $45
    Weed pulling (flower beds) - $30
    Hedge trimming - $60
    Tree removal (standard size) - $250 flat fee
    Fertilizer application: $55
    """
    with open(os.path.join(base_dir, "pricing_notes.txt"), "w") as f:
        f.write(pricing_content)

    # 2. Field Logs (Dirty CSV data)
    # Mapping:
    # Client A: mowing (45), weed pulling (30) = 75
    # Client B: hedge trimming (60), mowing (45) = 105
    # Client C: tree removal (250) = 250
    # Client D: mowing (45), mowing (45), fertilizer (55) = 145
    # Grand Total: 75 + 105 + 250 + 145 = 575
    csv_data = [
        ["Client_Name", "Services_Rendered"],
        ["John Doe", "lawn mowing, weed pulling"],
        ["Jane Smith", "Hedge trimming; lawn mowing"],
        ["Bob Johnson", "tree removal"],
        ["Alice Brown", "lawn mowing | lawn mowing | Fertilizer application"]
    ]

    with open(os.path.join(base_dir, "field_logs.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
