import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("audits", exist_ok=True)

    # Master Stock
    master_stock = [
        {"Drug": "Oxycodone", "Schedule": "II", "Manufacturer": "CelticPharma", "Start_Stock": 200},
        {"Drug": "Hydrocodone", "Schedule": "II", "Manufacturer": "USAMeds", "Start_Stock": 150},
        {"Drug": "Buprenorphine", "Schedule": "III", "Manufacturer": "GaelicHealth", "Start_Stock": 300},
        {"Drug": "Amoxicillin", "Schedule": "VI", "Manufacturer": "GenericCo", "Start_Stock": 500}
    ]
    with open("inventory/master_stock.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Drug", "Schedule", "Manufacturer", "Start_Stock"])
        writer.writeheader()
        writer.writerows(master_stock)

    # Shift Logs
    shift1 = [
        {"patient": "P01", "drug": "Oxycodone", "qty": 10},
        {"patient": "P02", "drug": "Hydrocodone", "qty": 30},
        {"patient": "P03", "drug": "Amoxicillin", "qty": 100}
    ]
    shift2 = [
        {"patient": "P04", "drug": "Oxycodone", "qty": 10},
        {"patient": "P05", "drug": "Hydrocodone", "qty": 20},
        {"patient": "P06", "drug": "Buprenorphine", "qty": 10},
        {"patient": "P07", "drug": "Amoxicillin", "qty": 100}
    ]
    with open("logs/shift_1.json", "w") as f:
        json.dump(shift1, f, indent=2)
    with open("logs/shift_2.json", "w") as f:
        json.dump(shift2, f, indent=2)

    # Math remaining: Oxy(180), Hydro(100), Bupre(290), Amox(300)
    # Physical Counts (injecting discrepancies)
    physical = {
        "Oxycodone": 178,     # -2 discrepancy
        "Hydrocodone": 100,   # match
        "Buprenorphine": 290, # match
        "Amoxicillin": 295    # -5 discrepancy
    }
    with open("audits/physical_counts.json", "w") as f:
        json.dump(physical, f, indent=2)

def build_turn_2():
    os.makedirs("requests", exist_ok=True)
    
    # XML Refills
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<requests>
    <request id="R101">
        <drug>Oxycodone</drug>
        <qty>25</qty>
    </request>
    <request id="R102">
        <drug>Hydrocodone</drug>
        <qty>40</qty>
    </request>
    <request id="R103">
        <drug>Hydrocodone</drug>
        <qty>20</qty>
    </request>
    <request id="R104">
        <drug>Buprenorphine</drug>
        <qty>60</qty>
    </request>
    <request id="R105">
        <drug>Buprenorphine</drug>
        <qty>40</qty>
    </request>
    <request id="R106">
        <drug>Amoxicillin</drug>
        <qty>100</qty>
    </request>
</requests>
"""
    with open("requests/new_refills.xml", "w") as f:
        f.write(xml_content)

def build_turn_3():
    os.makedirs("external", exist_ok=True)
    
    urgent_needs = {
        "urgent_transfer": [
            {"drug": "Hydrocodone", "requested_qty": 100},
            {"drug": "Amoxicillin", "requested_qty": 200},
            {"drug": "Oxycodone", "requested_qty": 50}
        ]
    }
    with open("external/urgent_needs.json", "w") as f:
        json.dump(urgent_needs, f, indent=2)

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
