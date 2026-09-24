import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    
    # recipes/yoga_glow_v1.json
    with open("recipes/yoga_glow_v1.json", "w") as f:
        json.dump({
            "Lavender Oil": 5, 
            "Coconut Oil": 20, 
            "Shea Butter": 10, 
            "Lye": 2
        }, f, indent=4)
        
    # vendors/status.txt
    with open("vendors/status.txt", "w") as f:
        f.write("APPROVED: PureNaturals, CocoLoco, SheaBest, ChemCorp, ScentCo, AromaOils\n")
        f.write("RED ZONE (BANNED): ToxChem, BioHarm, EcoWorst\n")
        
    # inventory/deliveries_wk1.csv
    wk1 = [
        ["Lot1", "Lavender Oil", "PureNaturals", "Region A", "98", "2024-09-01", "25"],
        ["Lot2", "Coconut Oil", "ToxChem", "Region C", "100", "2024-08-01", "100"],
        ["Lot3", "Coconut Oil", "CocoLoco", "Region A", "100", "2025-06-01", "50"],
        ["Lot4", "Shea Butter", "SheaBest", "Region B", "100", "2025-05-01", "30"],
        ["Lot5", "Lye", "ChemCorp", "Region C", "99", "2026-01-01", "10"],
        ["Lot6", "Lavender Oil", "ScentCo", "Region B", "92", "2024-11-01", "20"]
    ]
    with open("inventory/deliveries_wk1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Lot Number", "Ingredient", "Vendor", "Region", "Purity", "Expiration", "Quantity"])
        writer.writerows(wk1)
        
    # inventory/deliveries_wk2.csv
    wk2 = [
        ["Lot7", "Shea Butter", "SheaBest", "Region C", "100", "2025-08-01", "20"],
        ["Lot8", "Coconut Oil", "CocoLoco", "Region B", "100", "2025-07-01", "40"],
        ["Lot9", "Lavender Oil", "AromaOils", "Region B", "96", "2025-10-01", "15"],
        ["Lot10", "Lye", "ChemCorp", "Region A", "99", "2025-12-01", "5"]
    ]
    with open("inventory/deliveries_wk2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Lot Number", "Ingredient", "Vendor", "Region", "Purity", "Expiration", "Quantity"])
        writer.writerows(wk2)

def build_turn_2():
    os.makedirs("alerts", exist_ok=True)
    with open("alerts/fda_warning.txt", "w") as f:
        f.write("URGENT FDA WARNING:\nAll essential oils sourced from Region B have been flagged for micro-contaminants. Immediate halt on usage is required for any stock from this region.\n")
        
    # inventory/deliveries_wk3.csv
    wk3 = [
        ["Lot11", "Lavender Oil", "PureNaturals", "Region A", "99", "2025-02-01", "30"],
        ["Lot12", "Coconut Oil", "CocoLoco", "Region C", "100", "2025-09-01", "60"],
        ["Lot13", "Shea Butter", "SheaBest", "Region A", "100", "2025-10-01", "40"],
        ["Lot14", "Lye", "ChemCorp", "Region B", "99", "2026-02-01", "10"],
        ["Lot15", "Lavender Oil", "BioHarm", "Region A", "99", "2025-03-01", "50"],
        ["Lot16", "Lavender Oil", "ScentCo", "Region A", "94", "2025-04-01", "20"]
    ]
    with open("inventory/deliveries_wk3.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Lot Number", "Ingredient", "Vendor", "Region", "Purity", "Expiration", "Quantity"])
        writer.writerows(wk3)

def build_turn_3():
    os.makedirs("orders", exist_ok=True)
    with open("orders/rush_order.xml", "w") as f:
        f.write("""<order>
  <client>Liberal Arts College</client>
  <product>Yoga Glow</product>
  <batches>3</batches>
  <priority>URGENT</priority>
</order>
""")

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
