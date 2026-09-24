import os
import argparse
import csv
import json

def write_csv(path, headers, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def build_turn_1():
    os.makedirs("wishlist", exist_ok=True)
    os.makedirs("budget", exist_ok=True)
    os.makedirs("build_plan", exist_ok=True)

    headers = ["PartID", "Name", "Brand", "Price", "Compatibility", "SafetyRating"]
    
    engine_rows = [
        ["E1", "V8 Cold Air Intake", "SpeedDemon", 350, "2018 F-150 5.0L V8", "N/A"],
        ["E2", "V6 Turbo Kit", "BoostMaster", 1500, "2018 F-150 3.5L V6", "N/A"],
        ["E3", "V8 Heavy Duty Radiator", "TrailBreaker", 600, "2018 F-150 5.0L V8", "N/A"],
        ["E4", "V8 Premium Radiator", "CoolRunnings", 800, "2018 F-150 5.0L V8", "N/A"],
    ]
    write_csv("wishlist/engine.csv", headers, engine_rows)

    suspension_rows = [
        ["S1", "2-inch Lift Kit", "TrailBreaker", 1200, "All F-150", "N/A"],
        ["S2", "3-inch Offroad Lift", "TrailBreaker", 1500, "2018 F-150 5.0L V8", "N/A"],
        ["S3", "Premium Shocks", "BumpyRides", 1000, "2018 F-150 5.0L V8", "N/A"],
        ["S4", "Cheap Shocks", "RustyIron", 400, "2018 F-150 5.0L V8", "N/A"],
    ]
    write_csv("wishlist/suspension.csv", headers, suspension_rows)

    trans_rows = [
        ["T1", "Heavy Duty Cooler", "TrailBreaker", 300, "2018 F-150 5.0L V8", "N/A"],
        ["T2", "Standard Cooler", "CoolRunnings", 200, "2018 F-150 5.0L V8", "N/A"],
        ["T3", "Offroad Gearbox", "ShiftMax", 2500, "All F-150", "N/A"],
    ]
    write_csv("wishlist/transmission.csv", headers, trans_rows)

    interior_rows = [
        ["I1", "Canvas Seat Covers", "ToughMud", 150, "All F-150", "3"],
        ["I2", "Leather Seat Covers", "FancyPants", 400, "All F-150", "4"],
        ["I3", "Rubber Floor Mats", "ToughMud", 100, "All F-150", "5"],
    ]
    write_csv("wishlist/interior.csv", headers, interior_rows)

    exterior_rows = [
        ["EX1", "Steel Bumper", "TrailBreaker", 800, "2018 F-150 5.0L V8", "5"],
        ["EX2", "Winch", "PullMaster", 600, "All F-150", "4"],
        ["EX3", "Roof Rack", "TrailBreaker", 500, "All F-150", "3"],
    ]
    write_csv("wishlist/exterior.csv", headers, exterior_rows)

    electrical_rows = [
        ["EL1", "Light Bar", "TrailBreaker", 250, "All F-150", "N/A"],
        ["EL2", "Dual Battery Kit", "PowerMax", 450, "2018 F-150 5.0L V8", "N/A"],
    ]
    write_csv("wishlist/electrical.csv", headers, electrical_rows)

    with open("budget/finance.json", "w") as f:
        json.dump({"total_budget": 6500}, f)

def build_turn_2():
    os.makedirs("new_arrivals", exist_ok=True)
    headers = ["PartID", "Name", "Brand", "Price", "Compatibility", "SafetyRating"]
    kids_rows = [
        ["K1", "Kid Booster Seat", "SafeT", 800, "All F-150", "5"],
        ["K2", "Rear Bench Protector", "SoftPad", 300, "All F-150", "4"],
        ["K3", "Premium Kid Harness", "LockTight", 1200, "All F-150", "9"],
        ["K4", "Cheap Harness", "DangerZone", 50, "All F-150", "2"],
        ["K5", "Incompatible Seat", "SafeT", 100, "2020 F-250", "10"],
    ]
    write_csv("new_arrivals/interior_kids.csv", headers, kids_rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
