import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("gala_plan", exist_ok=True)

    artifacts = [
        {"id": "A01", "name": "Astor Family Tea Set", "era": "Gilded Age", "material": "Silver", "weight": 5.5},
        {"id": "A02", "name": "Liberty Bust Mini", "era": "Gilded Age", "material": "Bronze", "weight": 14.0},
        {"id": "A03", "name": "Opulent Vase", "era": "Victorian", "material": "Glass", "weight": 2.0},
        {"id": "A04", "name": "Wine Goblet", "era": "Victorian", "material": "Glass", "weight": 1.5},
        {"id": "A05", "name": "Hand Mirror", "era": "Victorian", "material": "Glass", "weight": 4.0},
        {"id": "A06", "name": "Chandelier Crystal", "era": "Victorian", "material": "Glass", "weight": 3.0}, # Trap: 4th glass, needs storage
        {"id": "A07", "name": "Civil War Musket", "era": "Civil War", "material": "Wood/Iron", "weight": 9.0},
        {"id": "A08", "name": "Robber Baron Pocket Watch", "era": "Gilded Age", "material": "Gold", "weight": 0.5},
        {"id": "A09", "name": "Dutch Settler Coin", "era": "Colonial", "material": "Silver", "weight": 1.2},
        {"id": "A10", "name": "Old City Hall Bell", "era": "Colonial", "material": "Bronze", "weight": 18.0}
    ]
    
    with open("inventory/artifacts.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "era", "material", "weight"])
        writer.writeheader()
        writer.writerows(artifacts)

    cases = [
        {"id": "C01", "type": "Cabinet", "max_weight": 40.0, "height_from_ground": 40},
        {"id": "C02", "type": "Pedestal", "max_weight": 30.0, "height_from_ground": 35},
        {"id": "C03", "type": "Wall", "max_weight": 15.0, "height_from_ground": 65},
        {"id": "C04", "type": "Cabinet", "max_weight": 35.0, "height_from_ground": 45},
        {"id": "C05", "type": "Pedestal", "max_weight": 20.0, "height_from_ground": 30},
        {"id": "C06", "type": "Wall", "max_weight": 12.0, "height_from_ground": 70}
    ]
    
    with open("logistics/cases.json", "w") as f:
        json.dump(cases, f, indent=4)

def build_turn_2():
    # Turn 2 inherits Turn 1's state automatically. We just inject new challenges.
    
    # Damaging two of the biggest/most useful cases
    # C01 (Cabinet, 40 max) and C05 (Pedestal, 20 max) are broken
    with open("logistics/damaged_cases.txt", "w") as f:
        f.write("C01\nC05\n")
        
    new_artifacts = [
        {"id": "N01", "name": "Socialite's Silk Dress", "era": "Gilded Age", "material": "Textile", "weight": 4.5},
        {"id": "N02", "name": "Iroquois Headdress", "era": "Pre-Colonial", "material": "Feather", "weight": 2.0}
    ]
    
    with open("inventory/new_arrivals.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "era", "material", "weight"])
        writer.writeheader()
        writer.writerows(new_artifacts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
