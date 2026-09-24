import os
import json
import csv

def build_env():
    # Create the data directory (Note: cwd is already assets/data_round_01_aligned_mix_800_0770/)
    os.makedirs("party_data", exist_ok=True)
    
    # 1. RSVPs with demographics and allergies
    rsvps_data = [
        ["Family_Name", "Adults", "Kids_Under_5", "Allergies"],
        ["Williams", 2, 2, "None"],        # 2 + 1 = 3 portions
        ["Jackson", 1, 1, "Peanuts"],      # 1 + 0.5 = 1.5 portions (Triggers peanut oil swap)
        ["Moore", 2, 0, "Shellfish"],      # 2 + 0 = 2 portions
        ["Taylor", 2, 3, "None"],          # 2 + 1.5 = 3.5 portions
    ]
    # Total portions = 3 + 1.5 + 2 + 3.5 = 10 portions
    
    with open("party_data/rsvps.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rsvps_data)

    # 2. Recipes (Ingredient amounts per 1 full adult portion)
    recipes_data = {
        "Jollof_Rice": {
            "tomatoes": 0.5,
            "onions": 0.25,
            "rice": 0.5,
            "peanut_oil": 0.1,  # Needs to be swapped to canola_oil
            "chicken": 0.4
        },
        "Spicy_Plantains": {
            "plantains": 0.5,
            "spices": 0.05
        }
    }
    # Total needs (for 10 portions):
    # tomatoes: 5.0, onions: 2.5, rice: 5.0, canola_oil: 1.0, chicken: 4.0, plantains: 5.0, spices: 0.5
    
    with open("party_data/recipes.json", "w") as f:
        json.dump(recipes_data, f, indent=4)

    # 3. Store Prices
    prices_data = {
        "Atlanta International Market": {
            "tomatoes": 1.20,      # 5.0 * 1.20 = 6.00
            "onions": 0.80,        # 2.5 * 0.80 = 2.00
            "rice": 1.00,          # 5.0 * 1.00 = 5.00
            "peanut_oil": 3.00,    # N/A
            "canola_oil": 2.50,    # 1.0 * 2.50 = 2.50
            "chicken": 3.00,       # 4.0 * 3.00 = 12.00
            "plantains": 0.90,     # 5.0 * 0.90 = 4.50
            "spices": 5.00         # 0.5 * 5.00 = 2.50
            # Total = 6+2+5+2.5+12+4.5+2.5 = 34.50
        },
        "Dekalb Farmers Market": {
            "tomatoes": 1.50,      # 5.0 * 1.50 = 7.50
            "onions": 0.70,        # 2.5 * 0.70 = 1.75
            "rice": 0.90,          # 5.0 * 0.90 = 4.50
            "peanut_oil": 2.80,    # N/A
            "canola_oil": 2.80,    # 1.0 * 2.80 = 2.80
            "chicken": 3.50,       # 4.0 * 3.50 = 14.00
            "plantains": 0.80,     # 5.0 * 0.80 = 4.00
            "spices": 4.00         # 0.5 * 4.00 = 2.00
            # Total = 7.5+1.75+4.5+2.8+14+4+2 = 36.55
        },
        "Downtown Grocer": {
            "tomatoes": 1.00,      # 5.0 * 1.00 = 5.00
            "onions": 1.00,        # 2.5 * 1.00 = 2.50
            "rice": 1.20,          # 5.0 * 1.20 = 6.00
            "peanut_oil": 3.50,    # N/A
            "canola_oil": 3.00,    # 1.0 * 3.00 = 3.00
            "chicken": 2.80,       # 4.0 * 2.80 = 11.20
            "plantains": 1.20,     # 5.0 * 1.20 = 6.00
            "spices": 6.00         # 0.5 * 6.00 = 3.00
            # Total = 5+2.5+6+3+11.2+6+3 = 36.70
        }
    }
    
    with open("party_data/prices.json", "w") as f:
        json.dump(prices_data, f, indent=4)

if __name__ == "__main__":
    build_env()
