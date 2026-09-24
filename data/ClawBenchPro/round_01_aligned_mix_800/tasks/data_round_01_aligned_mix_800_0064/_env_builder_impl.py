import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("client", exist_ok=True)
    os.makedirs("specs", exist_ok=True)
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # materials.json
    materials = {
        "M01": {"name": "Timber-X", "cost": 100, "carbon": 5, "rating": 8},
        "M02": {"name": "Eco-Steel", "cost": 300, "carbon": 15, "rating": 9},
        "M03": {"name": "Recycled-Glass", "cost": 150, "carbon": 2, "rating": 6},
        "M04": {"name": "Standard-Concrete", "cost": 80, "carbon": 25, "rating": 7},
        "M05": {"name": "Cheap-Wood", "cost": 50, "carbon": 4, "rating": 4}
    }
    with open("specs/materials.json", "w") as f:
        json.dump(materials, f, indent=4)

    # client brief
    brief_content = """
PROJECT ALPHA - INITIAL BRIEF
Date: October 14th
Prepared by: VP of Operations

Look, the client is very particular about this Eco-Resort. First and foremost, we cannot exceed a total material budget of $500,000. 
Secondly, because of their green initiative, the total carbon footprint for the entire material order must not exceed 10,000 units. 
Finally, for structural integrity in the mountain region, every single material used must have a structural rating of at least 6. If a vendor includes even one material with a rating lower than 6, reject their entire proposal.
"""
    with open("client/project_alpha_brief.txt", "w") as f:
        f.write(brief_content.strip())

    # Proposals Phase 1
    # Vendor A: Passes Turn 1. (Will fail Turn 2 due to Timber-X)
    with open("proposals/vendor_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M01", "1000"])
        writer.writerow(["M03", "1000"])

    # Vendor B: Fails Turn 1 (M05 rating is 4 < 6)
    with open("proposals/vendor_B.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M01", "1000"])
        writer.writerow(["M05", "1000"])

    # Vendor C: Passes Turn 1. (Cost 450k, Carbon 6000. Will pass Turn 2, fail Turn 3 due to shipping)
    with open("proposals/vendor_C.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M03", "3000"])

    # Vendor D: Fails Turn 1 (Carbon 15000 > 10000)
    with open("proposals/vendor_D.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M02", "1000"])


def build_turn_2():
    os.makedirs("proposals_phase2", exist_ok=True)
    
    # Urgent update
    update_content = """
URGENT: MACRO-ECONOMIC ADJUSTMENT
Due to recent funding cuts and inflation concerns, the board has mandated that the overall project budget ceiling for Project Alpha must be reduced by exactly 15% effective immediately. 
All evaluations moving forward (and any final selections) must adhere to this new tightened budget constraint. Other metric constraints remain unchanged.
"""
    with open("client/urgent_update.txt", "w") as f:
        f.write(update_content.strip())

    # Proposals Phase 2
    # Vendor F: Fails Carbon (16500)
    with open("proposals_phase2/vendor_F.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M03", "2000"])
        writer.writerow(["M04", "500"])

    # Vendor G: Passes Turn 2 (Cost 375k < 425k new budget, Carbon 5000. Passes Turn 3.)
    with open("proposals_phase2/vendor_G.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M03", "2500"])

    # Vendor H: Fails Turn 2 (Uses Timber-X M01)
    with open("proposals_phase2/vendor_H.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Material_ID", "Quantity"])
        writer.writerow(["M01", "1000"])


def build_turn_3():
    os.makedirs("logistics", exist_ok=True)
    
    # Shipping rates
    # C is West (1.2), G is North (1.05)
    with open("logistics/shipping_rates.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Vendor", "Region", "Multiplier"])
        writer.writerow(["vendor_A", "East", "1.1"])
        writer.writerow(["vendor_B", "West", "1.2"])
        writer.writerow(["vendor_C", "West", "1.2"])
        writer.writerow(["vendor_D", "North", "1.05"])
        writer.writerow(["vendor_F", "East", "1.1"])
        writer.writerow(["vendor_G", "North", "1.05"])
        writer.writerow(["vendor_H", "South", "1.15"])


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
