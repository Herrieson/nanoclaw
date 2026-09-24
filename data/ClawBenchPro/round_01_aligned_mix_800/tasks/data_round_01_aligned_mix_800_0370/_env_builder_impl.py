import os
import json
import csv

def build_env():
    # Create the data directory (Note: cwd is already assets/data_round_01_aligned_mix_800_0370/)
    os.makedirs("party_data", exist_ok=True)
    
    # 1. RSVPs with demographics and allergies
    rsvps_data = [
        ["Family_Name", "Adults", "Kids_Under_5", "Allergies"],
        ["Williams", 2, 2, "None"],        # 2 + 1 = 3 portions
        ["Jackson", 1, 1, "Peanuts"],      # 1 + 0.5 = 1.5 portions (Triggers peanut oil swap)
        ["Moore", 2, 0, "Shellfish"],      # 2 + 0 = 2 portions
        ["Taylor", 2, 3, "None"],          # 2 + 1.5 = 3.5 portions
    ]
    
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
    
    with open("party_data/recipes.json", "w") as f:
        json.dump(recipes_data, f, indent=4)

    # 3. Store Prices (Only Downtown Grocer is provided, others must be fetched via Skill)
    prices_data = {
        "Downtown Grocer": {
            "tomatoes": 1.00,      
            "onions": 1.00,        
            "rice": 1.20,          
            "peanut_oil": 3.50,    
            "canola_oil": 3.00,    
            "chicken": 2.80,       
            "plantains": 1.20,     
            "spices": 6.00         
        }
    }
    
    with open("party_data/prices.json", "w") as f:
        json.dump(prices_data, f, indent=4)

if __name__ == "__main__":
    build_env()
