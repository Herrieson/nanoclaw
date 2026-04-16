import os
import json
import csv

def build_env():
    base_dir = "assets/data_17"
    inv_dir = os.path.join(base_dir, "inventory")
    scripts_dir = os.path.join(base_dir, "scripts")
    
    os.makedirs(inv_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    # 1. Generate Q1 Inventory (CSV)
    q1_data = [
        ["Species", "Thickness_in", "Width_in", "Length_in", "Qty"],
        ["Cherry", "1", "6", "96", "4"],
        ["Walnut", "2", "8", "120", "2"],
        ["Maple", "1", "4", "48", "10"]
    ]
    with open(os.path.join(inv_dir, "q1_stock.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(q1_data)

    # 2. Generate Q2 Inventory (TSV with slightly different headers to test agent)
    q2_data = [
        ["Wood_Type", "Thick", "Wide", "Long", "Quantity"],
        ["Cherry", "1", "6", "48", "2"],
        ["Oak", "1", "5", "96", "5"],
        ["Walnut", "2", "8", "60", "1"]
    ]
    with open(os.path.join(inv_dir, "q2_scraps.tsv"), "w", newline="") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(q2_data)

    # 3. Generate New Shipment (JSON)
    json_data = [
        {"species": "Maple", "thickness": 1, "width": 4, "length": 96, "count": 5},
        {"species": "Oak", "thickness": 1, "width": 5, "length": 120, "count": 3}
    ]
    with open(os.path.join(inv_dir, "new_shipment.json"), "w") as f:
        json.dump(json_data, f, indent=2)

    # 4. Generate Cutlist (What he needs for the cabinet)
    cutlist_data = [
        ["Species", "Thickness_in", "Width_in", "Total_Linear_Inches_Needed"],
        ["Cherry", "1", "6", "600"],  # Has (96*4)+(48*2) = 384+96 = 480. Needs 120.
        ["Walnut", "2", "8", "240"],  # Has (120*2)+(60*1) = 240+60 = 300. Needs 0.
        ["Maple", "1", "4", "1000"], # Has (48*10)+(96*5) = 480+480 = 960. Needs 40.
        ["Oak", "1", "5", "800"]     # Has (96*5)+(120*3) = 480+360 = 840. Needs 0.
    ]
    with open(os.path.join(base_dir, "project_cutlist.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cutlist_data)

    # 5. Generate calculator.py
    calculator_script = """import argparse
import csv
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--cutlist", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.inventory):
        print(f"Error: Inventory file {args.inventory} not found.")
        return

    # Aggregate inventory
    inventory = {}
    with open(args.inventory, 'r') as f:
        reader = csv.DictReader(f)
        required_headers = ['Species', 'Thickness_in', 'Width_in', 'Length_in', 'Qty']
        if not all(h in reader.fieldnames for h in required_headers):
            print("Error: Inventory CSV missing required headers.")
            return
            
        for row in reader:
            key = (row['Species'], int(row['Thickness_in']), int(row['Width_in']))
            linear_inches = int(row['Length_in']) * int(row['Qty'])
            inventory[key] = inventory.get(key, 0) + linear_inches

    # Calculate deficit
    purchase_order = []
    with open(args.cutlist, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['Species'], int(row['Thickness_in']), int(row['Width_in']))
            needed = int(row['Total_Linear_Inches_Needed'])
            have = inventory.get(key, 0)
            if needed > have:
                purchase_order.append(f"{key[0]} {key[1]}x{key[2]}: need {needed - have} more linear inches")

    with open('purchase_order.txt', 'w') as f:
        if not purchase_order:
            f.write("Inventory sufficient. Nothing to buy.\\n")
        else:
            f.write("=== PURCHASE ORDER ===\\n")
            for item in purchase_order:
                f.write(item + "\\n")
    print("Purchase order generated successfully.")

if __name__ == "__main__":
    main()
"""
    with open(os.path.join(scripts_dir, "calculator.py"), "w") as f:
        f.write(calculator_script)

if __name__ == "__main__":
    build_env()
