import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("vendor_info", exist_ok=True)
    os.makedirs("rules", exist_ok=True)
    os.makedirs("warehouse_data", exist_ok=True)
    os.makedirs("planning", exist_ok=True)

    # Vendor Data - Only V_A and V_D are acceptable.
    vendors = {
        "V_A": {"name": "GreenLife Co", "union_status": True, "labor_score": 85},
        "V_B": {"name": "CheapPlastics Inc", "union_status": False, "labor_score": 95},
        "V_C": {"name": "MegaCorp", "union_status": True, "labor_score": 40},
        "V_D": {"name": "Local Laborers Org", "union_status": True, "labor_score": 75}
    }
    with open("vendor_info/suppliers.json", "w") as f:
        json.dump(vendors, f, indent=4)

    # Eco Rules
    with open("rules/eco_standards.txt", "w") as f:
        f.write("We are an eco-friendly space. STRICT BAN on any materials listed as 'PVC' or 'Lead'. Do not accept items with these materials.\n")

    # Manifest 1
    manifest_data = [
        ["id", "vendor", "material", "weight_kg"],
        ["i01", "V_A", "Wood", "1.1"],
        ["i02", "V_B", "Fabric", "0.5"],  # Bad vendor
        ["i03", "V_D", "PVC", "0.9"],     # Bad material
        ["i04", "V_A", "Fabric", "0.4"],
        ["i05", "V_C", "Wood", "1.2"],    # Bad vendor
        ["i06", "V_D", "Electronics", "2.0"]
    ]
    with open("warehouse_data/manifest_1.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(manifest_data)

def build_turn_2():
    # Simulate time passing, delete the old vendor info to enforce memory usage
    if os.path.exists("vendor_info/suppliers.json"):
        os.remove("vendor_info/suppliers.json")
    
    # New chemical ban
    with open("rules/urgent_council_ban.txt", "w") as f:
        f.write("CITY COUNCIL URGENT DIRECTIVE:\nEffective immediately, any products containing the chemical additive 'Phthalates' are strictly banned from community centers.\n")

    # New Delivery
    delivery_data = [
        ["id", "vendor", "material", "weight_kg", "chemical_additives"],
        ["i07", "V_A", "Plastic", "0.6", "BPA"],           # Safe (BPA not explicitly banned by council rule in this context, V_A is good)
        ["i08", "V_D", "Plastic", "0.7", "Phthalates"],    # Bad chemical
        ["i09", "V_B", "Wood", "1.0", "None"],             # Bad vendor (Agent must remember V_B is bad)
        ["i10", "V_A", "Fabric", "0.3", "None"],           # Safe
        ["i11", "V_E", "Wood", "1.5", "None"]              # Unknown vendor (Should be rejected based on T1 memory)
    ]
    with open("warehouse_data/delivery_C.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(delivery_data)

def build_turn_3():
    # Kit Designs
    kit_designs = {
        "Eco-Builder": {
            "requirements": {
                "Wood": 1,
                "Fabric": 1
            },
            "max_total_weight_kg": 1.6
        },
        "Tech-Crafter": {
            "requirements": {
                "Electronics": 1,
                "Plastic": 1
            },
            "max_total_weight_kg": 3.0
        }
    }
    with open("planning/kit_designs.json", "w") as f:
        json.dump(kit_designs, f, indent=4)

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
