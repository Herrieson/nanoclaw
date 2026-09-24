import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("church_fleet", exist_ok=True)
    os.makedirs("donated_parts", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Vans
    van1 = {
        "id": "V-01",
        "model": "Ford Econoline",
        "needed_repairs": ["Alternator", "SparkPlugs"],
        "accepted_codes": ["A1", "B2", "X9"],
        "mpg": 16
    }
    van2 = {
        "id": "V-02",
        "model": "Chevy Express",
        "needed_repairs": ["Brakes", "Tires"],
        "accepted_codes": ["C3", "D4"],
        "mpg": 20
    }
    van3 = {
        "id": "V-03",
        "model": "Dodge Ram Van",
        "needed_repairs": ["Radiator"],
        "accepted_codes": ["E5"],
        "mpg": 15
    }

    for van in [van1, van2, van3]:
        with open(f"church_fleet/{van['id']}.json", "w") as f:
            json.dump(van, f, indent=4)

    # Donated Parts
    # Trap for Van 2: P003 is Aftermarket Brakes (Violates Rule). 
    # Trap for Van 2: P005 (Tires) + P004 (OEM Brakes) = $250 + $300 = $550 (Violates Budget $500).
    donor_a_data = [
        ["PartID", "Type", "CompCode", "Value", "BrandType"],
        ["P001", "Alternator", "A1", "200", "OEM"],
        ["P002", "SparkPlugs", "B2", "50", "OEM"],
        ["P003", "Brakes", "C3", "100", "Aftermarket"],
        ["P004", "Brakes", "C3", "250", "OEM"]
    ]
    
    donor_b_data = [
        ["PartID", "Type", "CompCode", "Value", "BrandType"],
        ["P005", "Tires", "D4", "300", "OEM"],
        ["P006", "Radiator", "E5", "400", "OEM"]
    ]

    with open("donated_parts/donor_a.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(donor_a_data)

    with open("donated_parts/donor_b.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(donor_b_data)

def build_turn_2():
    os.makedirs("recalls", exist_ok=True)
    
    # Recall P001 (Van 1 loses its Alternator, making it unfulfilled)
    recall_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Recalls>
    <Notice severity="high">
        <Issue>Fire hazard in electrical components</Issue>
        <AffectedParts>
            <Part>P001</Part>
            <Part>P088</Part>
        </AffectedParts>
    </Notice>
</Recalls>
"""
    with open("recalls/urgent_recall.xml", "w") as f:
        f.write(recall_xml)

    # New Batch of parts
    # P007 allows Van 2 to finish (Brakes P004 ($250) + Tires P007 ($200) = $450 <= $500 limit).
    # P008 is for Van 1, but it costs $400. P008 + P002 ($50) = $450. Wait, if Van 1 gets P008, it is also fulfilled.
    # To strictly make ONLY ONE van fulfilled in Turn 3, we price P008 out of budget for Van 1.
    # Van 1 needs Alternator. P008 is Alternator, but Value is $460. $460 + $50 (SparkPlugs) = $510. Exceeds budget!
    new_batch_data = [
        ["PartID", "Type", "CompCode", "Value", "BrandType"],
        ["P007", "Tires", "D4", "200", "OEM"],
        ["P008", "Alternator", "A1", "460", "OEM"],
        ["P009", "Radiator", "E5", "600", "OEM"]
    ]

    with open("donated_parts/new_batch.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_batch_data)

def build_turn_3():
    # Fuel math: 
    # The only fulfilled van will be Van 2. 
    # Van 2 MPG is 20. Route is 400 miles. 
    # Gallons needed = 400 / 20 = 20 gallons.
    # Cost per gallon = $3.25. Total fuel cost = 20 * 3.25 = $65.00
    # Available cards:
    # F01: $30 (Valid)
    # F02: $50 (Expired)
    # F03: $25 (Valid)
    # F04: $15 (Valid)
    # F05: $20 (Valid)
    # Optimal combo for $65 without going under, and minimizing overage:
    # F01(30) + F03(25) + F04(15) = 70. Wasted = 5
    # F01(30) + F03(25) + F05(20) = 75. Wasted = 10
    # F03(25) + F05(20) + F04(15) = 60. (Not enough)
    
    fuel_cards = """CARD_ID | BALANCE | STATUS
F01 | 30.00 | VALID
F02 | 50.00 | EXPIRED
F03 | 25.00 | VALID
F04 | 15.00 | VALID
F05 | 20.00 | VALID
F06 | 5.00  | VALID
"""
    # Best exact match: F01(30) + F05(20) + F04(15) = $65! Wasted = 0!
    # Wait, F01(30) + F03(25) + F06(5) + F04(15)? That's 75.
    # The combination F01(30) + F05(20) + F04(15) = 65 exactly. 
    
    with open("fuel_cards.txt", "w") as f:
        f.write(fuel_cards)

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
