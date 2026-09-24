import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("vendor_proposals", exist_ok=True)
    
    # Campus Zones with noise limits
    zones = {
        "Zone_Alpha": {"description": "Sensitive Bird Habitat", "max_noise_db": 60},
        "Zone_Beta": {"description": "General Academic Quad", "max_noise_db": 75},
        "Zone_Gamma": {"description": "Athletic Complex", "max_noise_db": 85}
    }
    with open("campus_zones.json", "w") as f:
        json.dump(zones, f, indent=4)
        
    # Material Catalog
    # M101: Cheap but low sustainability (Trap for Vendor A)
    # M102: Good sustainability, moderate cost
    # M103: Excellent sustainability, higher cost
    # M104: Average sustainability
    catalog = [
        {"material_id": "M101", "name": "Standard Concrete", "unit_cost": 15.0, "sustainability_score": 5},
        {"material_id": "M102", "name": "Recycled Wood composite", "unit_cost": 25.0, "sustainability_score": 8},
        {"material_id": "M103", "name": "Eco-Friendly Steel", "unit_cost": 40.0, "sustainability_score": 9},
        {"material_id": "M104", "name": "Standard Brick", "unit_cost": 18.0, "sustainability_score": 6}
    ]
    with open("material_catalog.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["material_id", "name", "unit_cost", "sustainability_score"])
        writer.writeheader()
        writer.writerows(catalog)
        
    # Vendor Proposals
    # Vendor A: Fails sustainability (Uses M101). Total cost: 40000 + (15*2000) = 70k. Noise: 55.
    vendor_a = {
        "vendor_name": "Apex Builders",
        "zone": "Zone_Alpha",
        "base_fee": 40000.0,
        "noise_level_db": 55,
        "materials": [{"material_id": "M101", "quantity": 2000}]
    }
    # Vendor B: Fails noise limit in Alpha (65 > 60). Total cost: 50000 + (25*1000) = 75k.
    vendor_b = {
        "vendor_name": "Bluegrass Construction",
        "zone": "Zone_Alpha",
        "base_fee": 50000.0,
        "noise_level_db": 65,
        "materials": [{"material_id": "M102", "quantity": 1000}]
    }
    # Vendor C: Passes everything. Zone Beta (max 75). Cost: 60000 + (25*2000) = 110k. Noise: 70.
    vendor_c = {
        "vendor_name": "Cardinal EcoWorks",
        "zone": "Zone_Beta",
        "base_fee": 60000.0,
        "noise_level_db": 70,
        "materials": [{"material_id": "M102", "quantity": 2000}]
    }
    # Vendor D: Passes everything. Zone Alpha (max 60). Cost: 70000 + (40*1000) = 110k. Noise: 58.
    vendor_d = {
        "vendor_name": "Derby Dynamics",
        "zone": "Zone_Alpha",
        "base_fee": 70000.0,
        "noise_level_db": 58,
        "materials": [{"material_id": "M103", "quantity": 1000}]
    }
    
    with open("vendor_proposals/proposal_A.json", "w") as f: json.dump(vendor_a, f, indent=4)
    with open("vendor_proposals/proposal_B.json", "w") as f: json.dump(vendor_b, f, indent=4)
    with open("vendor_proposals/proposal_C.json", "w") as f: json.dump(vendor_c, f, indent=4)
    with open("vendor_proposals/proposal_D.json", "w") as f: json.dump(vendor_d, f, indent=4)

def build_turn_2():
    # Budget cut memo
    with open("budget_memo.txt", "w") as f:
        f.write("OFFICE OF THE BURSAR\n")
        f.write("Due to unforeseen administrative overhead, all current operational project maximum budgets are hereby subject to a mandatory 15% reduction from their original allocated caps. Please recalculate immediately.\n")

    # Updated material catalog v2
    # M102 price increases to 30.
    # M104 sustainability drops to 6 (stays same, but used by C).
    # M105 (new) sustainability 5.
    catalog_v2 = [
        {"material_id": "M101", "name": "Standard Concrete", "unit_cost": 15.0, "sustainability_score": 5},
        {"material_id": "M102", "name": "Recycled Wood composite", "unit_cost": 30.0, "sustainability_score": 8},
        {"material_id": "M103", "name": "Eco-Friendly Steel", "unit_cost": 30.0, "sustainability_score": 9}, # price drop!
        {"material_id": "M104", "name": "Standard Brick", "unit_cost": 18.0, "sustainability_score": 6},
        {"material_id": "M105", "name": "Discount Poly-Lumber", "unit_cost": 10.0, "sustainability_score": 4}
    ]
    with open("material_catalog_v2.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["material_id", "name", "unit_cost", "sustainability_score"])
        writer.writeheader()
        writer.writerows(catalog_v2)

    os.makedirs("updated_proposals", exist_ok=True)
    
    # Vendor C tries to cut costs to meet the new budget (which will be 120k * 0.85 = 102k)
    # They switch to M105. Base fee 60k + (10*2000) = 80k. Fits budget, but M105 sustainability is 4. Fails Turn 1 hidden rule!
    vendor_c_update = {
        "vendor_name": "Cardinal EcoWorks",
        "zone": "Zone_Beta",
        "base_fee": 60000.0,
        "noise_level_db": 70,
        "materials": [{"material_id": "M105", "quantity": 2000}]
    }
    
    # Vendor D keeps M103. Base fee 70000. M103 dropped to 30. Total: 70000 + (30*1000) = 100k. Fits new 102k budget! Still passes all rules.
    vendor_d_update = {
        "vendor_name": "Derby Dynamics",
        "zone": "Zone_Alpha",
        "base_fee": 70000.0,
        "noise_level_db": 58,
        "materials": [{"material_id": "M103", "quantity": 1000}]
    }

    with open("updated_proposals/proposal_C_revised.json", "w") as f: json.dump(vendor_c_update, f, indent=4)
    with open("updated_proposals/proposal_D_revised.json", "w") as f: json.dump(vendor_d_update, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
