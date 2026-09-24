import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    cocktails = [
        {
            "name": "Golden Margarita",
            "sale_price": 15.0,
            "prep_time_minutes": 2,
            "ingredients": {"Tequila": 50, "Limes": 20, "Agave": 10}
        },
        {
            "name": "Ruby Fizz",
            "sale_price": 18.0,
            "prep_time_minutes": 3,
            "ingredients": {"Premium Gin": 40, "Limes": 15, "Club Soda": 50, "Simple Syrup": 10}
        },
        {
            "name": "Minty Breeze",
            "sale_price": 14.0,
            "prep_time_minutes": 3,
            "ingredients": {"Rum": 50, "Mint": 5, "Simple Syrup": 15, "Club Soda": 50}
        },
        {
            "name": "Irish Wake",
            "sale_price": 16.0,
            "prep_time_minutes": 3,
            "ingredients": {"Vodka": 40, "Rum": 20, "Berries": 10}
        },
        {
            "name": "Berry Smash",
            "sale_price": 16.0,
            "prep_time_minutes": 3,
            "ingredients": {"Vodka": 50, "Berries": 15, "Ginger Beer": 50, "Simple Syrup": 10}
        },
        {
            "name": "Citrus Blast",
            "sale_price": 12.0,
            "prep_time_minutes": 2,
            "ingredients": {"Vodka": 40, "Limes": 30, "Simple Syrup": 15}
        },
        {
            "name": "Complex Old Fashioned",
            "sale_price": 25.0,
            "prep_time_minutes": 6,
            "ingredients": {"Premium Gin": 50, "Simple Syrup": 10, "Mint": 2}
        },
        {
            "name": "Island Time",
            "sale_price": 15.0,
            "prep_time_minutes": 4,
            "ingredients": {"Rum": 60, "Agave": 15, "Club Soda": 40}
        }
    ]
    with open("recipes/cocktails.json", "w") as f:
        json.dump(cocktails, f, indent=4)

    catalog = {
        "Vodka": {"price": 20.0, "volume_or_weight": 1000, "unit": "ml", "delivery_days": 2},
        "Rum": {"price": 18.0, "volume_or_weight": 1000, "unit": "ml", "delivery_days": 2},
        "Tequila": {"price": 30.0, "volume_or_weight": 1000, "unit": "ml", "delivery_days": 2},
        "Premium Gin": {"price": 35.0, "volume_or_weight": 750, "unit": "ml", "delivery_days": 2},
        "Limes": {"price": 5.0, "volume_or_weight": 500, "unit": "ml", "delivery_days": 1},
        "Mint": {"price": 4.0, "volume_or_weight": 100, "unit": "g", "delivery_days": 1},
        "Berries": {"price": 6.0, "volume_or_weight": 200, "unit": "g", "delivery_days": 1},
        "Simple Syrup": {"price": 10.0, "volume_or_weight": 1000, "unit": "ml", "delivery_days": 2},
        "Agave": {"price": 15.0, "volume_or_weight": 500, "unit": "ml", "delivery_days": 4},
        "Club Soda": {"price": 2.0, "volume_or_weight": 1000, "unit": "ml", "delivery_days": 1},
        "Ginger Beer": {"price": 3.0, "volume_or_weight": 1000, "unit": "ml", "delivery_days": 1}
    }
    with open("suppliers/catalog.json", "w") as f:
        json.dump(catalog, f, indent=4)

    stock_data = [
        ["Ingredient", "Amount", "Unit"],
        ["Rum", "1000", "ml"],
        ["Mint", "100", "g"],
        ["Simple Syrup", "500", "ml"],
        ["Club Soda", "2000", "ml"],
        ["Berries", "50", "g"]
    ]
    with open("inventory/stock.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(stock_data)

def build_turn_2():
    with open("suppliers/updates.txt", "w") as f:
        f.write("URGENT SUPPLIER NOTICE:\n")
        f.write("- 'Premium Gin' is caught in customs. Delivery time is now updated to 5 days.\n")
        f.write("- 'Limes' are completely out of stock due to a local blight. Unavailable for ordering.\n")

def build_turn_3():
    os.makedirs("vip_profiles", exist_ok=True)
    profile = {
        "table": 7,
        "allergies": ["Citrus", "Limes", "Mint"],
        "preferences": ["Sweet", "Berry", "Fizzy"],
        "alcohol_preference": "None (Mocktail)"
    }
    with open("vip_profiles/table_7.json", "w") as f:
        json.dump(profile, f, indent=4)

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
