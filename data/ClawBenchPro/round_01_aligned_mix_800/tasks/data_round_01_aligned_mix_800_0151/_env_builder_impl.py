import os
import argparse
import json

def build_turn_1():
    os.makedirs("project_specs", exist_ok=True)
    os.makedirs("vendor_quotes", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    with open("project_specs/materials.txt", "w") as f:
        f.write("Project Materials Requirement:\n- 100 Steel Pipes\n- 50 Gallons Paint\n- 200 Wood Planks\n- 500 Bolts\n")

    with open("project_specs/safety_rules.txt", "w") as f:
        f.write("Safety Guidelines for Construction:\n1. Paint must be strictly Lead-free.\n2. Wood Planks must be Treated.\n3. Steel Pipes must be Rust-free.\n4. Bolts must be Galvanized.\n")

    with open("vendor_quotes/A.csv", "w") as f:
        f.write("Item_Name,Specs,Unit_Cost\n")
        f.write("Heavy Steel Pipe,\"Rust-free, solid\",20\n")
        f.write("Artistic Paint,\"Bright colors, Contains lead traces\",10\n")
        f.write("Oak Wood Planks,\"Treated, premium grade\",15\n")
        f.write("Metal Bolts,\"Galvanized, standard size\",1\n")

    b_data = [
        {"material": "Steel Pipe", "details": "Rust-free finish", "price_per_unit": 25},
        {"material": "Paint", "details": "Lead-free, eco-friendly", "price_per_unit": 30},
        {"material": "Wood Plank", "details": "Untreated pine", "price_per_unit": 10},
        {"material": "Bolt", "details": "Galvanized coating", "price_per_unit": 2}
    ]
    with open("vendor_quotes/B.json", "w") as f:
        json.dump(b_data, f, indent=2)

    with open("vendor_quotes/C.txt", "w") as f:
        f.write("Yo Marcus, here is my quote.\nI can do Steel Pipes (they have some minor surface rust but look cool) for 15 bucks each.\nThe Paint is 100% Lead-free and will cost you 20 per gallon.\nWood Planks are Treated, going for 18 a piece.\nGalvanized Bolts are 1.20 each.\nCheers, Vendor C.\n")

def build_turn_2():
    os.makedirs("eco_updates/new_vendors", exist_ok=True)

    with open("eco_updates/eco_rules.txt", "w") as f:
        f.write("City Green Deal Mandate:\n- All Wood Planks used in public installations must have FSC Certification.\n")

    d_data = {
        "inventory": [
            {"name": "Wood Plank", "attributes": ["Treated", "FSC Certified"], "cost": 25}
        ]
    }
    with open("eco_updates/new_vendors/D.json", "w") as f:
        json.dump(d_data, f, indent=2)

    discounts = {
        "promotions": [
            {
                "condition": ["Heavy Steel Pipe from Vendor A", "Metal Bolts from Vendor A"],
                "discount_type": "percentage",
                "value": 20,
                "applies_to": "combined_cost_of_these_items"
            },
            {
                "condition": ["Paint from Vendor C", "Oak Wood Planks from Vendor A"],
                "discount_type": "percentage",
                "value": 15,
                "applies_to": "total_order"
            }
        ]
    }
    with open("eco_updates/discounts.json", "w") as f:
        json.dump(discounts, f, indent=2)

def build_turn_3():
    os.makedirs("audit_info", exist_ok=True)

    with open("audit_info/blacklist.txt", "w") as f:
        f.write("CITY ANTI-CORRUPTION ALERT:\nVendor A has been blacklisted across the city for severe safety violations in previous municipal projects. No purchases from Vendor A are permitted under any circumstances.\n")

    with open("audit_info/emergency_fund.txt", "w") as f:
        f.write("Note to self: Found exactly $1500 in the company emergency stash. Can be used if the project budget completely blows up.\n")

    template = {
        "final_total_cost": 0,
        "emergency_fund_used": 0,
        "blacklisted_vendors_removed": [],
        "purchases": [
            {
                "item": "",
                "vendor": "",
                "unit_price": 0,
                "quantity": 0,
                "total_item_cost": 0
            }
        ]
    }
    with open("audit_info/report_template.json", "w") as f:
        json.dump(template, f, indent=2)

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
