import os
import csv
import json

def build_env():
    base_dir = "assets/data_274"
    suppliers_dir = os.path.join(base_dir, "suppliers")
    
    os.makedirs(suppliers_dir, exist_ok=True)
    
    # 1. Create cutlist.csv
    cutlist_path = os.path.join(base_dir, "cutlist.csv")
    with open(cutlist_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Material", "Quantity"])
        writer.writerow(["2x4x8 Treated Pine", 50])
        writer.writerow(["4x4x10 Treated Pine", 12])
        writer.writerow(["Decking Screws (5lb)", 3])
        
    # 2. Create supplier 1 (JSON format)
    # Total: 50*4.25 (212.5) + 12*12.50 (150) + 3*35.00 (105) = 467.50
    lumber_jack_path = os.path.join(suppliers_dir, "lumber_jack.json")
    with open(lumber_jack_path, 'w') as f:
        json.dump({
            "2x4x8 Treated Pine": 4.25,
            "4x4x10 Treated Pine": 12.50,
            "Decking Screws (5lb)": 35.00,
            "Plywood 4x8": 25.00 # Extra item to test filtering
        }, f)
        
    # 3. Create supplier 2 (Messy Text format)
    # Total: 50*3.90 (195) + 12*15.00 (180) + 3*40.00 (120) = 495.00
    bobs_wood_path = os.path.join(suppliers_dir, "bobs_wood.txt")
    with open(bobs_wood_path, 'w') as f:
        f.write("Supplier: Bob's Wood\n")
        f.write("Prices for this week, valid until Friday:\n\n")
        f.write("- 2x4x8 Treated Pine : $3.90\n")
        f.write("- Wood Glue (1 Gal) : $18.50\n")
        f.write("- Decking Screws (5lb) : $40.00\n")
        f.write("- 4x4x10 Treated Pine : $15.00\n")

    # 4. Create supplier 3 (CSV format) - The Cheapest One
    # Total: 50*4.50 (225) + 12*11.00 (132) + 3*32.50 (97.5) = 454.50
    southern_timber_path = os.path.join(suppliers_dir, "southern_timber.csv")
    with open(southern_timber_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Price"])
        writer.writerow(["Decking Screws (5lb)", "32.50"])
        writer.writerow(["2x4x8 Treated Pine", "4.50"])
        writer.writerow(["Nails (1lb)", "4.00"])
        writer.writerow(["4x4x10 Treated Pine", "11.00"])

if __name__ == "__main__":
    build_env()
