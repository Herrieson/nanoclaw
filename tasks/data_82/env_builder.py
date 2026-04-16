import os
import csv

def build_env():
    base_dir = "assets/data_82"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create fashion trends file
    trends_path = os.path.join(base_dir, "fashion_trends.txt")
    with open(trends_path, "w", encoding="utf-8") as f:
        f.write("plaid\n")
        f.write("oversized sweater\n")
        f.write("ankle boots\n")
        f.write("denim jacket\n")

    # 2. Create inventory dumps directory
    dumps_dir = os.path.join(base_dir, "inventory_dumps")
    os.makedirs(dumps_dir, exist_ok=True)

    # File 1: Standard CSV
    csv1_path = os.path.join(dumps_dir, "apparel_stock_A.csv")
    with open(csv1_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["prod_id", "desc", "qty", "price"])
        writer.writerow(["A100", "Plaid Flannel Shirt", "15", "25.50"]) # Match: 382.50
        writer.writerow(["A101", "Basic White Tee", "50", "10.00"])
        writer.writerow(["A102", "Oversized Sweater Vest", "12", "30.00"]) # Match: 360.00
        writer.writerow(["A103", "Skinny Jeans", "20", "40.00"])
        writer.writerow(["A104", "Classic Denim Jacket", "5", "55.00"]) # Match: 275.00

    # File 2: Tab separated text file
    txt1_path = os.path.join(dumps_dir, "footwear_stock.txt")
    with open(txt1_path, "w", encoding="utf-8") as f:
        f.write("ProductID\tDescription\tQuantity\tUnitPrice\n")
        f.write("F200\tChunky Ankle Boots\t8\t45.00\n") # Match: 360.00
        f.write("F201\tRunning Sneakers\t15\t60.00\n")
        f.write("F202\tLeather Loafers\t10\t50.00\n")

    # File 3: Messy CSV (missing values, inconsistent case)
    csv2_path = os.path.join(dumps_dir, "clearance_stock.csv")
    with open(csv2_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "stock", "cost"])
        writer.writerow(["C300", "Red PLAID Skirt", "10", "15.00"]) # Match: 150.00
        writer.writerow(["C301", "Broken Item", "", "10.00"]) # Malformed
        writer.writerow(["C302", "Summer Dress", "5", "20.00"])
        writer.writerow(["", "Missing ID Plaid", "2", "10.00"]) # Match but missing ID, agent should handle it somehow, let's say ID is UNKNOWN or blank. Expected: 20.00

if __name__ == "__main__":
    build_env()
