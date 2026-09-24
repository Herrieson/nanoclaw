import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("guidelines", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Trap 1: MediCareCorp is approved in Turn 1, but will be suspended in Turn 2.
    # Trap 2: Expired items based on "2024-10-15".
    # Trap 3: FDA recall targets specific Lot numbers.
    
    with open("guidelines/approved_vendors.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["VendorName", "Status"])
        writer.writerow(["MediCareCorp", "Approved"])
        writer.writerow(["PharmaInc", "Approved"])
        writer.writerow(["HealthPlus", "Approved"])
        writer.writerow(["GlobalMeds", "Approved"])

    with open("guidelines/fda_recalls.txt", "w") as f:
        f.write("URGENT FDA NOTICE:\n")
        f.write("All medications with Lot numbers starting with the characters '7X' have been flagged for cross-contamination.\n")
        f.write("Do not dispense under any circumstances.\n")

    # inventory/batch_A.csv
    with open("inventory/batch_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["med_name", "vendor", "lot_num", "expiry_date", "age_min", "age_max", "quantity"])
        # Passes T1, Fails T2 (due to vendor)
        writer.writerow(["Amoxicillin", "MediCareCorp", "1A234", "2025-01-01", "5", "12", "500"])
        # Fails T1 (Recalled lot 7X)
        writer.writerow(["Ibuprofen", "PharmaInc", "7X999", "2025-06-01", "2", "15", "300"])
        # Fails T1 (Expired)
        writer.writerow(["Cough Syrup", "HealthPlus", "2B333", "2024-09-01", "5", "17", "150"])
        # Passes T1 and T2
        writer.writerow(["Bandages", "HealthPlus", "9Y888", "2026-01-01", "0", "99", "1000"])

    # inventory/batch_B.json
    batch_b = [
        {
            "med_name": "Inhaler",
            "vendor": "GlobalMeds",
            "lot_num": "8B11",
            "expiry_date": "2025-06-01",
            "age_min": 6,
            "age_max": 18,
            "quantity": 200
        },
        {
            "med_name": "Vitamins",
            "vendor": "SketchyCo",  # Fails T1 (Unapproved vendor)
            "lot_num": "9C33",
            "expiry_date": "2026-01-01",
            "age_min": 5,
            "age_max": 12,
            "quantity": 400
        },
        {
            "med_name": "Antihistamine",
            "vendor": "MediCareCorp", # Passes T1, Fails T2
            "lot_num": "5D44",
            "expiry_date": "2025-12-01",
            "age_min": 10,
            "age_max": 17,
            "quantity": 250
        }
    ]
    with open("inventory/batch_B.json", "w") as f:
        json.dump(batch_b, f, indent=4)


def build_turn_2():
    os.makedirs("new_shipments", exist_ok=True)
    
    # Memo suspending MediCareCorp
    with open("urgent_memo.txt", "w") as f:
        f.write("FROM: Hospital Administration\n")
        f.write("SUBJECT: IMMEDIATE SUSPENSION OF VENDOR\n\n")
        f.write("It has come to our attention that MediCareCorp has falsified their safety reports. ")
        f.write("Effective immediately, absolutely zero stock from MediCareCorp is to be used or deployed. ")
        f.write("Pull any existing stock from our delivery manifests.\n")

    # new_shipments/batch_C.csv
    with open("new_shipments/batch_C.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["med_name", "vendor", "lot_num", "expiry_date", "age_min", "age_max", "quantity"])
        # Fails T2 (Suspended vendor)
        writer.writerow(["Antibiotic", "MediCareCorp", "2D44", "2025-08-01", "10", "17", "100"])
        # Passes T2
        writer.writerow(["Painkiller", "GlobalMeds", "5E55", "2025-10-01", "8", "16", "400"])
        # Fails T2 (Recalled lot pattern 7X from T1 rules!)
        writer.writerow(["Eye Drops", "PharmaInc", "7X111", "2025-11-01", "5", "17", "200"])
        # Fails T2 (Adult only)
        writer.writerow(["Blood Pressure Med", "HealthPlus", "3C22", "2026-02-01", "18", "99", "50"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
