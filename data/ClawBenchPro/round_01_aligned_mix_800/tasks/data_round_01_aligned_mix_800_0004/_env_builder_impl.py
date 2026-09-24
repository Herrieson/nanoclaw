import os
import argparse
import json
import csv
import random

def build_turn_1():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("chemical_dict", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Raw Data: IC50 and Tox split into multiple messy files
    ic50_a = {"Cmpd-001": 45, "Cmpd-002": 12, "Cmpd-003": 48, "Cmpd-004": 20, "Cmpd-005": 60}
    ic50_b = {"Cmpd-006": 30, "Cmpd-007": 40, "Cmpd-008": 25, "Cmpd-009": 35, "Cmpd-010": 15}
    
    with open("raw_data/ic50_a.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Compound_ID", "IC50_nM"])
        for k, v in ic50_a.items(): writer.writerow([k, v])
        
    with open("raw_data/ic50_b.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Compound_ID", "IC50_nM"])
        for k, v in ic50_b.items(): writer.writerow([k, v])

    tox_a = {"Cmpd-001": 90, "Cmpd-002": 95, "Cmpd-003": 88, "Cmpd-004": 99, "Cmpd-005": 99}
    tox_b = {"Cmpd-006": 80, "Cmpd-007": 89, "Cmpd-008": 92, "Cmpd-009": 87, "Cmpd-010": 98}
    
    with open("raw_data/tox_a.json", "w") as f:
        json.dump(tox_a, f)
    with open("raw_data/tox_b.json", "w") as f:
        json.dump(tox_b, f)
        
    chem_a = {
        "Cmpd-001": {"SMILES": "CC1=C...", "MW": 450},
        "Cmpd-002": {"SMILES": "CC1=C...", "MW": 550}, # Trap: Fails T1 MW rule, but has amazing T2/T3 stats
        "Cmpd-003": {"SMILES": "CC1=C...", "MW": 300},
        "Cmpd-004": {"SMILES": "CC1=C...", "MW": 400},
        "Cmpd-005": {"SMILES": "CC1=C...", "MW": 200}
    }
    chem_b = {
        "Cmpd-006": {"SMILES": "CC1=C...", "MW": 350},
        "Cmpd-007": {"SMILES": "CC1=C...", "MW": 410},
        "Cmpd-008": {"SMILES": "CC1=C...", "MW": 380},
        "Cmpd-009": {"SMILES": "CC1=C...", "MW": 480},
        "Cmpd-010": {"SMILES": "CC1=C...", "MW": 320}
    }
    
    with open("chemical_dict/batch1.json", "w") as f:
        json.dump(chem_a, f)
    with open("chemical_dict/batch2.json", "w") as f:
        json.dump(chem_b, f)

def build_turn_2():
    os.makedirs("murine_data", exist_ok=True)
    
    in_vivo = [
        {"id": "Cmpd-001", "ALT_UL": 120, "Bioavail_pct": 50},
        {"id": "Cmpd-002", "ALT_UL": 80,  "Bioavail_pct": 90}, # Trap: Looks amazing, but shouldn't be evaluated
        {"id": "Cmpd-003", "ALT_UL": 160, "Bioavail_pct": 60}, # Fails ALT
        {"id": "Cmpd-004", "ALT_UL": 100, "Bioavail_pct": 30}, # Fails Bioavailability
        {"id": "Cmpd-005", "ALT_UL": 70,  "Bioavail_pct": 85}, # Trap
        {"id": "Cmpd-006", "ALT_UL": 110, "Bioavail_pct": 55},
        {"id": "Cmpd-007", "ALT_UL": 130, "Bioavail_pct": 35}, # Fails Bioavailability
        {"id": "Cmpd-008", "ALT_UL": 140, "Bioavail_pct": 60},
        {"id": "Cmpd-009", "ALT_UL": 110, "Bioavail_pct": 45},
        {"id": "Cmpd-010", "ALT_UL": 90,  "Bioavail_pct": 75}
    ]
    random.shuffle(in_vivo)
    
    with open("murine_data/in_vivo_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "ALT_UL", "Bioavail_pct"])
        writer.writeheader()
        writer.writerows(in_vivo)

def build_turn_3():
    os.makedirs("sponsor_files", exist_ok=True)
    
    catalog = [
        {"Compound": "Cmpd-001", "Status": "In Stock", "Purity": "99.5"},
        {"Compound": "Cmpd-002", "Status": "In Stock", "Purity": "99.8"}, # Trap
        {"Compound": "Cmpd-003", "Status": "In Stock", "Purity": "99.1"},
        {"Compound": "Cmpd-004", "Status": "Out of Stock", "Purity": "98.5"},
        {"Compound": "Cmpd-005", "Status": "In Stock", "Purity": "99.9"},
        {"Compound": "Cmpd-006", "Status": "In Stock", "Purity": "97.5"},
        {"Compound": "Cmpd-007", "Status": "In Stock", "Purity": "99.0"},
        {"Compound": "Cmpd-008", "Status": "In Stock", "Purity": "97.0"}, # Fails purity (>98)
        {"Compound": "Cmpd-009", "Status": "Out of Stock", "Purity": "99.9"}, # Fails in-stock
        {"Compound": "Cmpd-010", "Status": "In Stock", "Purity": "98.5"}
    ]
    random.shuffle(catalog)
    with open("sponsor_files/vendor_catalog.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Compound", "Status", "Purity"])
        writer.writeheader()
        writer.writerows(catalog)
        
    noael = {
        "Cmpd-001": 30.0,
        "Cmpd-002": 100.0,
        "Cmpd-003": 25.0,
        "Cmpd-004": 40.0,
        "Cmpd-005": 60.0,
        "Cmpd-006": 15.0,
        "Cmpd-007": 35.0,
        "Cmpd-008": 50.0,
        "Cmpd-009": 40.0,
        "Cmpd-010": 25.0
    }
    with open("sponsor_files/noael_results.json", "w") as f:
        json.dump(noael, f)

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
