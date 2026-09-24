import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("artists", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("specs", exist_ok=True)

    # Roster Trap: 
    # To get avg > 85, you need high vibe scores. 
    # High vibe scores are usually expensive.
    roster_data = [
        ["artist_id", "name", "medium", "rate", "vibe_score"],
        ["A01", "Jaxson", "Muralist", 12000, 92],
        ["A02", "Chloe", "Muralist", 8000, 80],
        ["A03", "Zane", "Digital", 15000, 95],
        ["A04", "Elara", "Digital", 9000, 88],
        ["A05", "Viper", "Digital", 6000, 75], # Cheap but tank vibe
        ["A06", "Mia", "Print", 10000, 82],
        ["A07", "Leo", "Print", 14000, 89]
    ]

    with open("artists/roster.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(roster_data)

    # Vendor Trap: GreenPrint Co is cheap and A-rated. Perfect for Turn 1!
    # ElitePress is A-rated but expensive.
    # CheapPress is C-rated (fails constraint).
    vendors_data = [
        {
            "vendor_id": "V01",
            "name": "ElitePress",
            "base_fee": 6000,
            "eco_rating": "A",
            "ink_type": "Standard"
        },
        {
            "vendor_id": "V02",
            "name": "GreenPrint Co",
            "base_fee": 3000,
            "eco_rating": "A",
            "ink_type": "Eco-Ink V1"
        },
        {
            "vendor_id": "V03",
            "name": "CheapPress",
            "base_fee": 1500,
            "eco_rating": "C",
            "ink_type": "Standard"
        },
        {
            "vendor_id": "V04",
            "name": "CityPrint Labs",
            "base_fee": 5000,
            "eco_rating": "A-",
            "ink_type": "Standard"
        }
    ]

    with open("vendors/directory.json", "w", encoding="utf-8") as f:
        json.dump(vendors_data, f, indent=4)

def build_turn_2():
    # Budget was 45000. 15% cut -> 38250.
    # Backup vendors introduced.
    backup_vendors = [
        {
            "vendor_id": "V05",
            "name": "EcoPress V2",
            "base_fee": 4500,
            "eco_rating": "A-",
            "ink_type": "Eco-Ink V2"
        },
        {
            "vendor_id": "V06",
            "name": "NaturePrint",
            "base_fee": 7000,
            "eco_rating": "A+",
            "ink_type": "Standard"
        }
    ]
    with open("vendors/backup_vendors.json", "w", encoding="utf-8") as f:
        json.dump(backup_vendors, f, indent=4)

def build_turn_3():
    # Color profiles spec
    color_profiles = {
        "standard_mural": "CMYK",
        "standard_digital": "RGB",
        "standard_print": "CMYK",
        "eco_v2_override": {
            "target": "Print",
            "profile": "Pantone-Eco"
        }
    }
    with open("specs/color_profiles.json", "w", encoding="utf-8") as f:
        json.dump(color_profiles, f, indent=4)

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
