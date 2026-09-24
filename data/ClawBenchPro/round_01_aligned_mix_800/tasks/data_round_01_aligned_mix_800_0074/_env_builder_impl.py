import os
import argparse
import json
import csv
import xml.etree.ElementTree as ET

def build_turn_1():
    os.makedirs("db", exist_ok=True)
    os.makedirs("incoming", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("audit", exist_ok=True)

    policies = {
        "roof": {"limit": 15000, "deductible": 1000},
        "water": {"limit": 8000, "deductible": 500},
        "equipment": {"limit": 12000, "deductible": 200}
    }
    with open("db/policies.json", "w") as f:
        json.dump(policies, f, indent=4)

    client_history = [
        {"ClientID": "C001", "PriorClaimsTotal": 10000, "AnnualCap": 50000},
        {"ClientID": "C002", "PriorClaimsTotal": 18000, "AnnualCap": 20000},
        {"ClientID": "C003", "PriorClaimsTotal": 5000, "AnnualCap": 15000},
        {"ClientID": "C004", "PriorClaimsTotal": 2000, "AnnualCap": 30000}
    ]
    with open("db/client_history.json", "w") as f:
        json.dump(client_history, f, indent=4)

    with open("db/blacklist.txt", "w") as f:
        f.write("C003\nC009\n")

    batch_1 = [
        {"ClaimID": "CLM101", "ClientID": "C001", "Category": "roof", "ClaimAmount": 14000},
        {"ClaimID": "CLM102", "ClientID": "C002", "Category": "water", "ClaimAmount": 4000},
        {"ClaimID": "CLM103", "ClientID": "C003", "Category": "equipment", "ClaimAmount": 5000},
        {"ClaimID": "CLM104", "ClientID": "C004", "Category": "equipment", "ClaimAmount": 15000}
    ]
    
    with open("incoming/claims_batch_1.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ClaimID", "ClientID", "Category", "ClaimAmount"])
        writer.writeheader()
        writer.writerows(batch_1)

def build_turn_2():
    os.makedirs("incoming", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    root = ET.Element("Claims")
    claims_data = [
        {"id": "CLM201", "client": "C001", "cat": "avian_damage", "amt": "12000"},
        {"id": "CLM202", "client": "C002", "cat": "roof", "amt": "5000"},
        {"id": "CLM203", "client": "C004", "cat": "water", "amt": "3000"}
    ]
    for c in claims_data:
        claim_node = ET.SubElement(root, "Claim")
        ET.SubElement(claim_node, "ClaimID").text = c["id"]
        ET.SubElement(claim_node, "ClientID").text = c["client"]
        ET.SubElement(claim_node, "Category").text = c["cat"]
        ET.SubElement(claim_node, "ClaimAmount").text = c["amt"]

    tree = ET.ElementTree(root)
    tree.write("incoming/claims_batch_2.xml")

    with open("docs/avian_supplement.txt", "w") as f:
        f.write("AVIAN STRIKE SUPPLEMENTARY POLICY:\n")
        f.write("For any claim with category 'avian_damage', there is NO standard deductible.\n")
        f.write("Instead, we only cover 50% of the initial ClaimAmount.\n")
        f.write("The maximum category limit for avian_damage is flatly capped at $5000 per claim.\n")
        f.write("All annual client cap rules still apply as normal.\n")

def build_turn_3():
    os.makedirs("audit", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    audit_data = [
        {"Category": "roof", "MaxReinsuranceLimit": 15000},
        {"Category": "water", "MaxReinsuranceLimit": 4000},
        {"Category": "equipment", "MaxReinsuranceLimit": 10000},
        {"Category": "avian_damage", "MaxReinsuranceLimit": 5000}
    ]
    with open("audit/reinsurance_audit.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Category", "MaxReinsuranceLimit"])
        writer.writeheader()
        writer.writerows(audit_data)

    with open("docs/manager_notes.txt", "w") as f:
        f.write("Maria, please ensure you read the reinsurance limits carefully.\n")
        f.write("If the sum of our approved payouts for a specific category exceeds the limit,\n")
        f.write("you must multiply each claim's approved amount in that category by a reduction factor:\n")
        f.write("(MaxReinsuranceLimit / TotalApprovedForCategory).\n")
        f.write("If the category total is less than or equal to the limit, do not touch the claim amounts.\n")

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
