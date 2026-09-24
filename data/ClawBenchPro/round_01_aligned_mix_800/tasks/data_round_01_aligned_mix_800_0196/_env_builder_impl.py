import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Vendor A: CSV format
    # Columns: item_id, name, category, cost, retail, stock, weight_lbs
    vendor_a_data = [
        ["A101", "Deluxe Grill", "BBQ", 100.0, 200.0, 20, 50.0], # Margin 50%, stock 20. Valid.
        ["A102", "Charcoal Bag", "BBQ", 10.0, 15.0, 50, 20.0],   # Margin 33.3%, stock 50. Damage 36 -> stock 14. Invalid (<15).
        ["A103", "Patio Chair", "Outdoor", 30.0, 38.0, 40, 15.0],# Margin 21%. Invalid (<25%).
        ["A104", "Smoker Pro", "BBQ", 150.0, 250.0, 18, 80.0],   # Margin 40%, stock 18. Valid.
        ["A105", "Tiki Torch", "Outdoor", 5.0, 10.0, 100, 2.0]   # Margin 50%, stock 100. Valid.
    ]
    with open("inventory/vendor_a.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "name", "category", "cost", "retail", "stock", "weight_lbs"])
        writer.writerows(vendor_a_data)

    # Vendor B: JSON format
    # Keys: id, productName, cat, wholesale, msrp, qty, lbs
    vendor_b_data = [
        {"id": "B201", "productName": "Cooler 50L", "cat": "Outdoor", "wholesale": 45.0, "msrp": 70.0, "qty": 30, "lbs": 12.0}, # Margin 35.7%, stock 30. Valid. (Turn 3 note: 20% off -> 56. Margin: 11/56=19.6% > 10%)
        {"id": "B202", "productName": "Grill Brush", "cat": "BBQ", "wholesale": 2.0, "msrp": 8.0, "qty": 60, "lbs": 1.0},       # Margin 75%. Valid.
        {"id": "B203", "productName": "Lawn Mower", "cat": "Garden", "wholesale": 100.0, "msrp": 150.0, "qty": 20, "lbs": 60.0},# Wrong category. Invalid.
        {"id": "B204", "productName": "Meat Thermometer", "cat": "BBQ", "wholesale": 18.0, "msrp": 24.0, "qty": 40, "lbs": 0.5},# Margin 25%, stock 40. Damage 5 -> 35. Valid. (Turn 3 note: 20% off -> 19.2. Margin 1.2/19.2=6.25% < 10%. Cap at wholesale/0.9 = 20.0)
        {"id": "B205", "productName": "Folding Table", "cat": "Outdoor", "wholesale": 30.0, "msrp": 45.0, "qty": 25, "lbs": 25.0} # Margin 33%. Valid. Will be recalled.
    ]
    with open("inventory/vendor_b.json", "w") as f:
        json.dump(vendor_b_data, f, indent=2)

    # Damage Log: Unstructured text
    damage_text = """Shift Report - Warehouse Manager
    
Last night was a mess. The forklift guys were racing again. 
They backed into a pallet of Charcoal Bags (item A102) and completely ruined 36 bags. 
Also, someone dropped a box of Meat Thermometers (item B204) and 5 of them shattered.
We also had 2 Smoker Pros (A104) with scratched paint, but we'll still sell them at full price so don't deduct them.
"""
    with open("logs/damage_log.txt", "w") as f:
        f.write(damage_text)

def build_turn_2():
    os.makedirs("urgent", exist_ok=True)
    os.makedirs("store", exist_ok=True)

    # Recall Notice
    recall_data = [
        ["recalled_id", "reason"],
        ["B205", "Legs collapse under heavy weight"],
        ["A101", "Faulty gas valve - FIRE HAZARD"]
    ]
    with open("urgent/recall.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(recall_data)

    # Aisle weight limits
    aisles_data = {
        "Aisle_1": 1500.0,
        "Aisle_2": 800.0,
        "Aisle_3": 500.0
    }
    with open("store/aisles.json", "w") as f:
        json.dump(aisles_data, f, indent=2)

def build_turn_3():
    # Turn 3 requires no new files, but we create a dummy file to simulate environmental progression
    os.makedirs("store", exist_ok=True)
    with open("store/tax_memo.txt", "w") as f:
        f.write("Reminder: Kentucky State Sales Tax is 6.00%.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
