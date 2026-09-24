import os
import argparse
import json
import csv
import xml.etree.ElementTree as ET

def build_turn_1():
    # Create directories
    os.makedirs("ward_a_patients", exist_ok=True)
    os.makedirs("medical_refs", exist_ok=True)
    os.makedirs("garden_catalog", exist_ok=True)

    # 1. Ward A Patients (JSON)
    patients_a = [
        {"id": "A1", "name": "Mr. Smith", "age": 78, "medications": ["Lisinopril", "Aspirin"]},
        {"id": "A2", "name": "Mrs. Higgins", "age": 82, "medications": ["Metformin", "Vitamin D"]},
        {"id": "A3", "name": "Mr. Davis", "age": 69, "medications": ["Atorvastatin", "Omeprazole"]}
    ]
    for p in patients_a:
        with open(f"ward_a_patients/patient_{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

    # 2. Herb Contraindications (CSV) - Contains traps for Turn 2
    contraindications = [
        ["Herb", "Medication", "Risk_Level"],
        ["Licorice Root", "Lisinopril", "High"],
        ["Ginseng", "Metformin", "Severe"],
        ["St. John's Wort", "Atorvastatin", "Moderate"],
        ["Spinach", "Warfarin", "Severe"],
        ["Kale", "Warfarin", "Severe"],
        ["Chamomile", "Ibuprofen", "Moderate"],
        ["Rosemary", "Aspirin", "Low"],
        ["Thyme", "Penicillin", "Low"]
    ]
    with open("medical_refs/herb_contraindications.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(contraindications)

    # 3. Spring Seeds Catalog (XML)
    # Target lowest safe cost: Spinach (8) + Basil (12) + Mint (15) = 35.
    # Trap: Spinach is extremely cheap and perfectly safe in Turn 1, but deadly in Turn 2.
    root = ET.Element("Catalog", season="Spring")
    seeds = [
        {"name": "Mint", "cost": "15", "difficulty": "2"},
        {"name": "Basil", "cost": "12", "difficulty": "1"},
        {"name": "Lavender", "cost": "22", "difficulty": "3"},
        {"name": "Spinach", "cost": "8", "difficulty": "1"},
        {"name": "Licorice Root", "cost": "10", "difficulty": "2"},
        {"name": "Rosemary", "cost": "18", "difficulty": "4"}
    ]
    for s in seeds:
        item = ET.SubElement(root, "Seed")
        ET.SubElement(item, "Name").text = s["name"]
        ET.SubElement(item, "Cost").text = s["cost"]
        ET.SubElement(item, "Difficulty").text = s["difficulty"]
    
    tree = ET.ElementTree(root)
    tree.write("garden_catalog/spring_seeds.xml")

def build_turn_2():
    # Directories might already exist if framework copies workspace, but we ensure existence for new ones
    os.makedirs("ward_b_patients", exist_ok=True)
    os.makedirs("updates", exist_ok=True)
    os.makedirs("garden_catalog", exist_ok=True)

    # 1. Ward B Patients (JSON)
    patients_b = [
        {"id": "B1", "name": "Mrs. Clark", "age": 71, "medications": ["Ibuprofen", "Calcium"]},
        {"id": "B2", "name": "Mr. Lewis", "age": 88, "medications": ["Amlodipine"]}
    ]
    for p in patients_b:
        with open(f"ward_b_patients/patient_{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

    # 2. Updates (TXT)
    with open("updates/ward_a_changes.txt", "w") as f:
        f.write("URGENT MEDICAL UPDATE:\n")
        f.write("Mrs. Higgins (Patient A2) experienced a TIA last night.\n")
        f.write("Orders from Dr. Evans:\n")
        f.write("- Discontinue Metformin immediately.\n")
        f.write("- Begin Warfarin 5mg daily to manage clotting risk.\n")
        f.write("Please update all charts and dietary plans accordingly.\n")

    # 3. Summer Seeds Catalog (JSON)
    # Agent needs 2 more seeds to reach 4 (since Spinach is discarded, leaving Mint and Basil).
    # Safe options for Ward A & B combined: Thyme, Oregano, Parsley.
    # Lowest cost for 2 safe summer seeds: Parsley (9) + Thyme (10) = 19.
    summer_seeds = [
        {"name": "Thyme", "cost": 10, "difficulty": 2},
        {"name": "Oregano", "cost": 14, "difficulty": 2},
        {"name": "Parsley", "cost": 9, "difficulty": 1},
        {"name": "Kale", "cost": 7, "difficulty": 1},      # Unsafe (Warfarin)
        {"name": "Chamomile", "cost": 13, "difficulty": 2} # Unsafe (Ibuprofen)
    ]
    with open("garden_catalog/summer_seeds.json", "w") as f:
        json.dump(summer_seeds, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
