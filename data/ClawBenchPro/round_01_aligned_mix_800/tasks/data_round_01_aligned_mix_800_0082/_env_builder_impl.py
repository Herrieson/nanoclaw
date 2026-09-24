import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("ward_data", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    patients = [
        ["id", "name", "age", "diet_code", "allergies", "mobility_status"],
        ["P01", "John Smith", "65", "D1", "None", "Walking"],
        ["P02", "Alice Johnson", "72", "D2", "dairy", "Bedbound"],
        ["P03", "Robert Davis", "58", "D3", "nuts", "Wheelchair"],
        ["P04", "Emma Brown", "81", "D1", "None", "Walking"],
        ["P05", "Michael Miller", "45", "D2", "None", "Walking"]
    ]
    with open("ward_data/patients.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(patients)

    codes = (
        "Diet Codes Explanation:\n"
        "D1: Standard Diabetic Diet\n"
        "D2: Renal Diet (Requires Renal_Supplement)\n"
        "D3: Liquid Diet (Requires Liquid_Supplement)\n"
    )
    with open("ward_data/codes.txt", "w") as f:
        f.write(codes)

    catalog = [
        {"item_name": "Renal_Supp_A", "type": "Renal_Supplement", "contains_allergens": ["dairy", "soy"]},
        {"item_name": "Renal_Supp_B", "type": "Renal_Supplement", "contains_allergens": ["gluten"]},
        {"item_name": "Liquid_Supp_X", "type": "Liquid_Supplement", "contains_allergens": ["nuts", "dairy"]},
        {"item_name": "Liquid_Supp_Y", "type": "Liquid_Supplement", "contains_allergens": []}
    ]
    with open("inventory/catalog.json", "w") as f:
        json.dump(catalog, f, indent=4)

    stock = {
        "Renal_Supp_A": 20,
        "Renal_Supp_B": 5,
        "Liquid_Supp_X": 10,
        "Liquid_Supp_Y": 2
    }
    with open("inventory/stock.json", "w") as f:
        json.dump(stock, f, indent=4)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 陷阱: 新来的海地病人 P06, 对 soy 过敏。需要 Renal。
    new_patients = [
        ["id", "name", "age", "diet_code", "allergies", "mobility_status"],
        ["P06", "Jean Baptiste", "68", "D2", "soy", "Bedbound"],
        ["P07", "Sarah Connor", "40", "D3", "None", "Walking"]
    ]
    with open("updates/new_patients.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_patients)

    # 陷阱: Renal_Supp_B 最便宜，但不适合 P06 (如果是买别的)。
    # 稍微调整：旧 catalog 里 Renal_Supp_B 含 gluten，适合 P06 和 P02。
    # 现在给新品牌定价。
    new_prices = [
        {"item_name": "Renal_Supp_B", "price": 4.0, "allergen_traces": ["gluten"]},
        {"item_name": "Renal_Supp_C", "price": 2.5, "allergen_traces": ["soy"]}, # 最便宜，但 P06 过敏
        {"item_name": "Renal_Supp_D", "price": 6.0, "allergen_traces": []},
        {"item_name": "Liquid_Supp_Y", "price": 5.0, "allergen_traces": []},
        {"item_name": "Liquid_Supp_Z", "price": 3.0, "allergen_traces": ["nuts"]} # P03 对 nuts 过敏
    ]
    with open("updates/new_prices.json", "w") as f:
        json.dump(new_prices, f, indent=4)

def build_turn_3():
    os.makedirs("staff", exist_ok=True)
    
    trainings = [
        ["staff_id", "name", "certifications"],
        ["S01", "Nancy Wheeler", "Dietary_Safety;Basic_CPR"],
        ["S02", "Steve Harrington", "Dietary_Safety;Allergy_Care;Basic_CPR"],
        ["S03", "Robin Buckley", "Allergy_Care"],
        ["S04", "Dustin Henderson", "Dietary_Safety;Allergy_Care"]
    ]
    with open("staff/trainings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(trainings)

    # 陷阱: S01 只照顾了 P02 (有过敏)，缺 Allergy_Care。 S03 照顾了 P06 (新来的老乡，有过敏)，缺 Dietary_Safety。
    schedule = {
        "Monday_Shift": [
            {"staff_id": "S01", "assigned_patients": ["P01", "P02", "P04"]},
            {"staff_id": "S02", "assigned_patients": ["P03"]},
            {"staff_id": "S03", "assigned_patients": ["P05", "P06"]},
            {"staff_id": "S04", "assigned_patients": ["P07"]}
        ]
    }
    with open("staff/schedule.json", "w") as f:
        json.dump(schedule, f, indent=4)

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
