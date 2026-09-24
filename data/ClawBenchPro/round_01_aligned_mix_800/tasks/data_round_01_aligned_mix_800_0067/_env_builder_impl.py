import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("crew_data", exist_ok=True)
    os.makedirs("shifts", exist_ok=True)
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Roster
    roster_data = [
        ["WorkerID", "Name", "Tier", "Diet", "BaseRate"],
        ["W01", "Carlos", "1", "None", "30.0"],
        ["W02", "Maria", "2", "Vegetarian", "25.0"],
        ["W03", "Luis", "1", "No Pork", "35.0"],
        ["W04", "Jose", "2", "None", "22.0"],
        ["W05", "Ana", "1", "Vegetarian", "32.0"]
    ]
    with open("crew_data/roster.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(roster_data)

    # 2. Weekday Shifts (Mon-Fri)
    mon_to_fri = {
        "W01": [8, 10, 8, 8, 8], # Tier 1: 42 hrs total (2 hrs daily OT on Tue)
        "W02": [10, 10, 10, 10, 0], # Tier 2: 40 hrs total (0 OT)
        "W03": [8, 8, 8, 8, 8], # Tier 1: 40 hrs total (0 OT)
        "W04": [8, 9, 8, 9, 8], # Tier 2: 42 hrs total (2 hrs weekly OT)
        "W05": [8, 8, 8, 8, 0]  # Tier 1: 32 hrs total
    }
    with open("shifts/mon_to_fri.json", "w") as f:
        json.dump(mon_to_fri, f, indent=4)

    # 3. Planned Weekend Shifts
    sat_sun_plan = {
        "W01": [0, 0],
        "W02": [8, 0],
        "W03": [8, 8],
        "W04": [0, 8],
        "W05": [0, 0]
    }
    with open("shifts/sat_sun_plan.json", "w") as f:
        json.dump(sat_sun_plan, f, indent=4)

    # 4. Recipes
    dishes = {
        "Tacos de Carnitas": {"Pork": 2, "Tortilla": 3, "Onion": 1},
        "Quesadilla": {"Cheese": 2, "Tortilla": 2},
        "Pollo Asado": {"Chicken": 2, "Rice": 1, "Beans": 1},
        "Ensalada Mixta": {"Lettuce": 2, "Tomato": 2},
        "Burrito de Res": {"Beef": 2, "Tortilla": 1, "Beans": 1, "Cheese": 1}
    }
    with open("recipes/dishes.json", "w") as f:
        json.dump(dishes, f, indent=4)

    # 5. Prices V1
    prices_v1 = [
        ["Ingredient", "PricePerUnit"],
        ["Pork", "2.0"],
        ["Tortilla", "0.5"],
        ["Onion", "0.5"],
        ["Cheese", "1.5"],
        ["Chicken", "2.5"],
        ["Rice", "0.5"],
        ["Beans", "0.5"],
        ["Lettuce", "1.0"],
        ["Tomato", "1.0"],
        ["Beef", "3.0"]
    ]
    with open("recipes/prices_v1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(prices_v1)


def build_turn_2():
    # Assume previous files exist, just inject updates
    
    # Actual Weekend Shifts
    actual_weekend = {
        "W01": [8, 0], # Called in for emergency
        "W02": [0, 0], # Rained out
        "W03": [10, 8], # Extra hours
        "W04": [8, 8], # Extra hours
        "W05": [10, 10] # Surprise massive shift
    }
    with open("shifts/actual_weekend.json", "w") as f:
        json.dump(actual_weekend, f, indent=4)

    # Prices V2 (Inflation)
    prices_v2 = [
        ["Ingredient", "PricePerUnit"],
        ["Pork", "3.0"], # Jumped
        ["Tortilla", "0.8"], # Jumped
        ["Onion", "0.5"],
        ["Cheese", "2.0"],
        ["Chicken", "2.5"],
        ["Rice", "0.6"],
        ["Beans", "0.6"],
        ["Lettuce", "1.5"],
        ["Tomato", "1.5"],
        ["Beef", "4.0"]
    ]
    with open("recipes/prices_v2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(prices_v2)


def build_turn_3():
    os.makedirs("invoices", exist_ok=True)
    
    # Receipts from market
    receipts = [
        ["Item", "QuantityBought", "TotalPaid"],
        ["Pork", "5", "16.0"], # Actual spend might differ slightly from calculated
        ["Tortilla", "10", "8.0"],
        ["Cheese", "4", "9.0"],
        ["Rice", "2", "1.5"],
        ["Beans", "2", "1.5"],
        ["Lettuce", "4", "7.0"],
        ["Tomato", "4", "6.0"],
        ["Chicken", "4", "11.0"]
    ]
    with open("invoices/mercado_receipts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(receipts)


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
