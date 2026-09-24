import os
import argparse
import csv
import json

def build_turn_1():
    # Inventory
    os.makedirs("sales_team", exist_ok=True)
    os.makedirs("inquiries", exist_ok=True)
    
    inventory_data = [
        ["item_id", "mineral_name", "purity", "origin", "stock_tons", "base_price"],
        ["ITM-001", "Lithium Ore", "92", "Australia", "500", "1200"],
        ["ITM-002", "Lithium Ore", "96", "Chile", "300", "1500"],
        ["ITM-003", "Malachite", "85", "Congo", "50", "4000"],
        ["ITM-004", "Malachite", "75", "Zambia", "100", "3000"],
        ["ITM-005", "Vanadinite", "90", "Morocco", "20", "8500"],
        ["ITM-006", "Vanadinite", "95", "Morocco", "10", "9200"],
        ["ITM-007", "Cobalt", "98", "Congo", "200", "2500"],
        ["ITM-008", "Cobalt", "99", "China", "150", "2700"],
        ["ITM-009", "Cobalt", "94", "China", "400", "2100"],
        ["ITM-010", "Bauxite", "60", "Brazil", "1000", "300"],
    ]
    with open("inventory.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # Sales team
    reps = {
        "REP-A": {"name": "Alice", "base_rate": 0.05},
        "REP-B": {"name": "Bob", "base_rate": 0.04},
        "REP-C": {"name": "Charlie", "base_rate": 0.06}
    }
    with open("sales_team/reps.json", "w") as f:
        json.dump(reps, f, indent=2)

    policy_text = """
MEMO - Commission Rules
I can never remember this, so here it is:
1. Start with the rep's base rate.
2. If the mineral being sold contains "Lithium" in its name, add an extra 1.5% (0.015) to their rate because of the EV boom.
3. Calculate the commission = Total Order Value * Final Rate.
4. If the Total Order Value is strictly greater than $500,000, add a flat $5000 bonus on top of their calculated commission.
- David
"""
    with open("sales_team/commission_policy.txt", "w") as f:
        f.write(policy_text)

    # Inquiries
    inq1 = {"inquiry_id": "INQ-101", "rep_id": "REP-A", "mineral_name": "Lithium Ore", "required_purity_min": 90, "requested_tons": 200}
    inq2 = {"inquiry_id": "INQ-102", "rep_id": "REP-B", "mineral_name": "Malachite", "required_purity_min": 80, "requested_tons": 40}
    inq3 = {"inquiry_id": "INQ-103", "rep_id": "REP-C", "mineral_name": "Cobalt", "required_purity_min": 95, "requested_tons": 100}
    inq4 = {"inquiry_id": "INQ-104", "rep_id": "REP-A", "mineral_name": "Vanadinite", "required_purity_min": 85, "requested_tons": 15} # Will take ITM-005
    inq5 = {"inquiry_id": "INQ-105", "rep_id": "REP-B", "mineral_name": "Bauxite", "required_purity_min": 80, "requested_tons": 500} # Fails purity

    for i, data in enumerate([inq1, inq2, inq3, inq4, inq5]):
        with open(f"inquiries/req_{i}.json", "w") as f:
            json.dump(data, f)

def build_turn_2():
    os.makedirs("compliance", exist_ok=True)
    os.makedirs("urgent_inquiries", exist_ok=True)

    compliance_text = """
URGENT: COMPLIANCE UPDATE
Effective immediately, the following restrictions apply to all sales:
- ALL minerals originating from "Congo" are RESTRICTED.
- ANY mineral from "China" with a purity STRICTLY LESS THAN 95 is RESTRICTED.
Do not fulfill any orders using inventory that falls under these restrictions.
"""
    with open("compliance/restricted_origins.txt", "w") as f:
        f.write(compliance_text)

    # Inquiries that test compliance and remaining stock
    inq6 = {"inquiry_id": "INQ-106", "rep_id": "REP-C", "mineral_name": "Cobalt", "required_purity_min": 90, "requested_tons": 50} 
    # China 94 is restricted. Congo is restricted. Must use China 99 (ITM-008)
    inq7 = {"inquiry_id": "INQ-107", "rep_id": "REP-A", "mineral_name": "Lithium Ore", "required_purity_min": 90, "requested_tons": 400} 
    # ITM-001 had 500, INQ-101 took 200, so 300 left. Fails. ITM-002 has 300. Fails. Must reject.
    inq8 = {"inquiry_id": "INQ-108", "rep_id": "REP-B", "mineral_name": "Malachite", "required_purity_min": 70, "requested_tons": 20}
    # ITM-003 is Congo (restricted). Must use ITM-004.

    for i, data in enumerate([inq6, inq7, inq8]):
        with open(f"urgent_inquiries/urg_{i}.json", "w") as f:
            json.dump(data, f)

def build_turn_3():
    os.makedirs("returns", exist_ok=True)
    os.makedirs("wife_hobby", exist_ok=True)

    returns_data = {
        "INQ-102": 40,  # Returned Malachite (ITM-003)
        "INQ-104": 15   # Returned Vanadinite (ITM-005)
    }
    with open("returns/return_manifest.json", "w") as f:
        json.dump(returns_data, f, indent=2)

    wishlist_text = """
Wife's Wishlist:
She mentioned she's really looking for "Vanadinite" from "Morocco". 
Any purity is fine. I need to get her a piece to calm her down about my long hours.
"""
    with open("wife_hobby/wishlist.txt", "w") as f:
        f.write(wishlist_text)

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
