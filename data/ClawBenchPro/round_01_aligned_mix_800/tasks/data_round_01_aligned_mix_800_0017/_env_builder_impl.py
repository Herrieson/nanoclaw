import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("routes", exist_ok=True)
    os.makedirs("parts", exist_ok=True)

    routes = {
        "stage_1": {
            "A1": {"dist": 100, "toll": 10},
            "A2": {"dist": 120, "toll": 0}
        },
        "stage_2": {
            "B1": {"dist": 200, "toll": 20},
            "B2": {"dist": 150, "toll": 5}
        },
        "stage_3": {
            "C1": {"dist": 100, "toll": 15},
            "C2": {"dist": 140, "toll": 0}
        }
    }
    with open("routes/base_routes.json", "w") as f:
        json.dump(routes, f, indent=4)

    vendors_data = [
        ["node", "part_type", "part_id", "price", "weight_g", "condition"],
        ["A1", "Engine", "E1", 80, 400, "Mint"],
        ["A1", "Cabin", "C1", 70, 500, "Good"],
        ["A2", "Frame", "F1", 60, 550, "Mint"],
        ["A2", "Wheels", "W1", 30, 200, "Good"],
        ["B1", "Frame", "F2", 90, 600, "Mint"],
        ["B1", "Engine", "E2", 110, 420, "Mint"],
        ["B2", "Cabin", "C2", 85, 480, "Mint"],
        ["B2", "Wheels", "W2", 40, 250, "Mint"],
        ["C1", "Wheels", "W3", 50, 230, "Good"],
        ["C1", "Frame", "F3", 100, 600, "Mint"],
        ["C2", "Cabin", "C3", 60, 450, "Good"],
        ["C2", "Engine", "E3", 75, 410, "Mint"],
        # Distractions with Poor condition
        ["A1", "Wheels", "W_poor", 10, 200, "Poor"],
        ["B2", "Frame", "F_poor", 50, 500, "Poor"]
    ]
    with open("parts/vendors.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(vendors_data)

def build_turn_2():
    os.makedirs("news_update", exist_ok=True)
    with open("news_update/urgent_msg.txt", "w") as f:
        f.write("FRAUD ALERT: The vendor at A1 selling Cabin parts has been identified as a scammer. Your transaction has been reversed and the money refunded to your account. Do not expect the part to arrive.\n")

    detour_routes = {
        "stage_3_detour": {
            "D1": {"dist": 120, "toll": 10},
            "D2": {"dist": 160, "toll": 0}
        }
    }
    with open("routes/detour_routes.json", "w") as f:
        json.dump(detour_routes, f, indent=4)

    detour_vendors = [
        ["node", "part_type", "part_id", "price", "weight_g", "condition"],
        ["D1", "Cabin", "C4", 80, 500, "Mint"],
        ["D1", "Frame", "F4", 85, 450, "Good"],
        ["D1", "Frame", "F6", 70, 550, "Good"], # Trap: cheaper but causes overweight
        ["D2", "Cabin", "C5", 60, 400, "Mint"],
        ["D2", "Frame", "F5", 90, 650, "Mint"]  # Trap: causes overweight
    ]
    with open("parts/detour_vendors.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(detour_vendors)

def build_turn_3():
    os.makedirs("finance", exist_ok=True)
    template = """# EXPENSE REIMBURSEMENT FORM

**Driver:** Jake
**Vehicle:** Company Rig

## Route Summary
- Total Miles Driven: [INSERT TOTAL MILES] miles
- Total Tolls Paid: $[INSERT TOTAL TOLLS]

## Reimbursement Calculation
- Gas Allowance (@ $0.50/mile): $[INSERT GAS ALLOWANCE]
- Tolls Reimbursement: $[INSERT TOLLS REIMBURSEMENT]
-----------------------------------------
**GRAND TOTAL TO BE REIMBURSED:** $[INSERT GRAND TOTAL]
"""
    with open("finance/invoice_template.md", "w") as f:
        f.write(template)

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
